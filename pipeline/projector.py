import re

def get_nested_value(obj, path):
    if not path:
        return obj
    
    array_match = re.match(r'^(.+?)\[(\d+|\*)\]$', path)
    if array_match:
        base_path = array_match.group(1)
        index = array_match.group(2)
        
        value = get_nested_value(obj, base_path)
        if not isinstance(value, list):
            return None
        
        if index == '*':
            return value
        else:
            idx = int(index)
            return value[idx] if idx < len(value) else None
    
    parts = path.split('.', 1)
    key = parts[0]
    
    if not isinstance(obj, dict) or key not in obj:
        return None
    
    if len(parts) == 1:
        return obj[key]
    else:
        return get_nested_value(obj[key], parts[1])

def apply_normalization(value, normalize_type):
    if normalize_type == 'E164' and isinstance(value, str):
        return value
    elif normalize_type == 'canonical' and isinstance(value, str):
        return value
    return value

def project_candidate(candidate, config):
    output = {}
    
    field_configs = config.get('fields', [])
    on_missing = config.get('on_missing', 'null')
    include_confidence = config.get('include_confidence', False)
    
    if not field_configs:
        output = candidate.copy()
    else:
        for field_config in field_configs:
            output_path = field_config.get('path')
            source_path = field_config.get('from', output_path)
            required = field_config.get('required', False)
            normalize = field_config.get('normalize')
            
            if '[].' in source_path:
                parts = source_path.split('[].')
                base_path = parts[0]
                field_name = parts[1]
                items = get_nested_value(candidate, base_path)
                if isinstance(items, list):
                    value = [item.get(field_name) for item in items if isinstance(item, dict)]
                else:
                    value = None
            elif source_path.endswith('[]'):
                base_path = source_path[:-2]
                items = get_nested_value(candidate, base_path)
                if isinstance(items, list):
                    value = items
                else:
                    value = None
            else:
                value = get_nested_value(candidate, source_path)
            
            if value is None or value == [] or value == {}:
                if required and on_missing == 'error':
                    raise ValueError(f"Required field '{output_path}' is missing")
                elif on_missing == 'omit':
                    continue
                else:
                    value = None
            
            if normalize and value is not None:
                value = apply_normalization(value, normalize)
            
            output[output_path] = value
    
    if include_confidence and 'provenance' in candidate:
        output['provenance'] = candidate['provenance']
        output['overall_confidence'] = candidate.get('overall_confidence', 0.0)
    
    return output

def project_candidates(candidates, config):
    return [project_candidate(c, config) for c in candidates]
