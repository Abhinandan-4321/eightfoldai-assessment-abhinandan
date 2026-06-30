SOURCE_TYPE_CONFIDENCE = {
    'csv': 0.85,
    'json': 0.85,
    'txt': 0.60
}

def calculate_field_confidence(candidate, field_name):
    source_types = candidate.get('source_types', [candidate.get('source_type', 'txt')])
    
    if field_name in ['emails', 'phones']:
        values = candidate.get(field_name, [])
        if not values:
            return 0.0
        if isinstance(values[0], dict) and 'confidence' in values[0]:
            return sum(v['confidence'] for v in values) / len(values)
        return max(SOURCE_TYPE_CONFIDENCE.get(st, 0.5) for st in source_types)
    
    if field_name == 'skills':
        skills = candidate.get('skills', [])
        if not skills:
            return 0.0
        return sum(s['confidence'] for s in skills) / len(skills)
    
    if field_name == 'location':
        location = candidate.get('location', {})
        return location.get('country_confidence', 0.7)
    
    value = candidate.get(field_name)
    if value is None or value == '' or value == []:
        return 0.0
    
    base_confidence = max(SOURCE_TYPE_CONFIDENCE.get(st, 0.5) for st in source_types)
    
    if len(source_types) > 1:
        base_confidence = min(0.95, base_confidence + 0.15)
    
    return base_confidence

def add_confidence_scores(candidate):
    provenance = {}
    
    fields_to_score = [
        'candidate_id', 'full_name', 'emails', 'phones', 'location',
        'links', 'headline', 'years_experience', 'skills', 'experience', 'education'
    ]
    
    for field in fields_to_score:
        confidence = calculate_field_confidence(candidate, field)
        sources = candidate.get('sources', [candidate.get('source', 'unknown')])
        
        provenance[field] = {
            'source': sources if isinstance(sources, list) else [sources],
            'method': 'structured' if 'csv' in candidate.get('source_types', []) else 'heuristic',
            'confidence': round(confidence, 2)
        }
    
    candidate['provenance'] = provenance
    
    field_confidences = [p['confidence'] for p in provenance.values() if p['confidence'] > 0]
    if field_confidences:
        candidate['overall_confidence'] = round(sum(field_confidences) / len(field_confidences), 2)
    else:
        candidate['overall_confidence'] = 0.0
    
    return candidate
