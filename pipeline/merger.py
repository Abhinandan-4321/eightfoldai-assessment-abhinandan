import hashlib

SOURCE_PRIORITY = {
    'csv': 0.85,
    'json': 0.85,
    'txt': 0.60
}

def generate_candidate_id(name, email):
    key = f"{name.lower().strip()}:{email.lower().strip()}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]

def get_match_key(candidate):
    emails = [e['value'] if isinstance(e, dict) else e for e in candidate.get('emails', [])]
    primary_email = emails[0] if emails else ''
    name = candidate.get('full_name', '').lower().strip()
    phones = [p['value'] if isinstance(p, dict) else p for p in candidate.get('phones', [])]
    
    return {
        'name': name,
        'email': primary_email.lower().strip(),
        'phones': set(phones)
    }

def candidates_match(cand1, cand2):
    key1 = get_match_key(cand1)
    key2 = get_match_key(cand2)
    
    if key1['email'] and key2['email'] and key1['email'] == key2['email']:
        return True
    
    if key1['name'] and key2['name'] and key1['name'] == key2['name']:
        if key1['phones'] and key2['phones'] and key1['phones'] & key2['phones']:
            return True
    
    return False

def merge_lists(list1, list2, key_field=None):
    if key_field:
        seen = set()
        merged = []
        for item in list1 + list2:
            key = item.get(key_field) if isinstance(item, dict) else item
            if key and key not in seen:
                seen.add(key)
                merged.append(item)
        return merged
    else:
        seen = set()
        merged = []
        for item in list1 + list2:
            val = item['value'] if isinstance(item, dict) else item
            if val not in seen:
                seen.add(val)
                merged.append(item)
        return merged

def merge_skills(skills1, skills2):
    skill_map = {}
    
    for skill in skills1:
        name = skill['name']
        if name not in skill_map:
            skill_map[name] = skill.copy()
        else:
            skill_map[name]['sources'].extend(skill['sources'])
            skill_map[name]['confidence'] = max(skill_map[name]['confidence'], skill['confidence'])
    
    for skill in skills2:
        name = skill['name']
        if name not in skill_map:
            skill_map[name] = skill.copy()
        else:
            skill_map[name]['sources'].extend(skill['sources'])
            skill_map[name]['confidence'] = max(skill_map[name]['confidence'], skill['confidence'])
    
    for name in skill_map:
        skill_map[name]['sources'] = list(set(skill_map[name]['sources']))
        if len(skill_map[name]['sources']) > 1:
            skill_map[name]['confidence'] = min(0.95, skill_map[name]['confidence'] + 0.15)
    
    return list(skill_map.values())

def merge_two_candidates(cand1, cand2):
    priority1 = SOURCE_PRIORITY.get(cand1.get('source_type', 'txt'), 0.5)
    priority2 = SOURCE_PRIORITY.get(cand2.get('source_type', 'txt'), 0.5)
    
    primary = cand1 if priority1 >= priority2 else cand2
    secondary = cand2 if priority1 >= priority2 else cand1
    
    merged = {
        'sources': [cand1.get('source'), cand2.get('source')],
        'source_types': [cand1.get('source_type'), cand2.get('source_type')]
    }
    
    merged['full_name'] = primary.get('full_name') or secondary.get('full_name')
    
    merged['emails'] = merge_lists(
        cand1.get('emails', []),
        cand2.get('emails', [])
    )
    
    merged['phones'] = merge_lists(
        cand1.get('phones', []),
        cand2.get('phones', [])
    )
    
    loc1 = cand1.get('location', {})
    loc2 = cand2.get('location', {})
    merged['location'] = {
        'city': loc1.get('city') or loc2.get('city'),
        'region': loc1.get('region') or loc2.get('region'),
        'country': loc1.get('country') or loc2.get('country'),
        'country_confidence': max(loc1.get('country_confidence', 0), loc2.get('country_confidence', 0))
    }
    
    links1 = cand1.get('links', {})
    links2 = cand2.get('links', {})
    merged['links'] = {
        'linkedin': links1.get('linkedin') or links2.get('linkedin'),
        'github': links1.get('github') or links2.get('github'),
        'portfolio': links1.get('portfolio') or links2.get('portfolio'),
        'other': list(set((links1.get('other', []) + links2.get('other', []))))
    }
    
    merged['headline'] = primary.get('headline') or secondary.get('headline')
    
    years1 = cand1.get('years_experience')
    years2 = cand2.get('years_experience')
    if years1 is not None and years2 is not None:
        merged['years_experience'] = years1 if priority1 >= priority2 else years2
    else:
        merged['years_experience'] = years1 if years1 is not None else years2
    
    merged['skills'] = merge_skills(
        cand1.get('skills', []),
        cand2.get('skills', [])
    )
    
    exp_map = {}
    for exp in cand1.get('experience', []) + cand2.get('experience', []):
        key = (exp.get('company', '').lower(), exp.get('title', '').lower())
        if key not in exp_map or not exp_map[key].get('summary'):
            exp_map[key] = exp
    merged['experience'] = list(exp_map.values())
    
    edu_map = {}
    for edu in cand1.get('education', []) + cand2.get('education', []):
        key = (edu.get('institution', '').lower(), edu.get('degree', '').lower())
        if key not in edu_map:
            edu_map[key] = edu
    merged['education'] = list(edu_map.values())
    
    return merged

def merge_candidates(candidates):
    if not candidates:
        return []
    
    merged_candidates = []
    processed = set()
    
    for i, cand1 in enumerate(candidates):
        if i in processed:
            continue
        
        current_merged = cand1
        processed.add(i)
        
        for j, cand2 in enumerate(candidates[i+1:], start=i+1):
            if j in processed:
                continue
            
            if candidates_match(current_merged, cand2):
                current_merged = merge_two_candidates(current_merged, cand2)
                processed.add(j)
        
        merged_candidates.append(current_merged)
    
    for candidate in merged_candidates:
        emails = [e['value'] if isinstance(e, dict) else e for e in candidate.get('emails', [])]
        primary_email = emails[0] if emails else 'unknown@example.com'
        candidate['candidate_id'] = generate_candidate_id(
            candidate.get('full_name', 'Unknown'),
            primary_email
        )
    
    return merged_candidates
