import csv

def extract_from_csv(filepath):
    candidates = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                candidate = {
                    'source': filepath,
                    'source_type': 'csv',
                    'raw_data': row
                }
                
                candidate['full_name'] = row.get('name', '').strip()
                candidate['emails'] = [row.get('email', '').strip()] if row.get('email', '').strip() else []
                candidate['phones'] = [row.get('phone', '').strip()] if row.get('phone', '').strip() else []
                
                location_parts = {}
                if row.get('location'):
                    parts = [p.strip() for p in row.get('location', '').split(',')]
                    if len(parts) >= 1:
                        location_parts['city'] = parts[0]
                    if len(parts) >= 2:
                        location_parts['region'] = parts[1]
                    if len(parts) >= 3:
                        location_parts['country'] = parts[2]
                candidate['location'] = location_parts
                
                links = {}
                if row.get('linkedin'):
                    links['linkedin'] = row.get('linkedin').strip()
                if row.get('github'):
                    links['github'] = row.get('github').strip()
                if row.get('portfolio'):
                    links['portfolio'] = row.get('portfolio').strip()
                candidate['links'] = links
                
                candidate['headline'] = row.get('title', '').strip() or None
                
                years_exp = row.get('years_exp') or row.get('years_experience')
                if years_exp:
                    try:
                        candidate['years_experience'] = float(years_exp)
                    except ValueError:
                        candidate['years_experience'] = None
                else:
                    candidate['years_experience'] = None
                
                skills_str = row.get('skills', '')
                if skills_str:
                    candidate['skills'] = [s.strip() for s in skills_str.split(',') if s.strip()]
                else:
                    candidate['skills'] = []
                
                experience = []
                if row.get('current_company') and row.get('title'):
                    experience.append({
                        'company': row.get('current_company').strip(),
                        'title': row.get('title').strip(),
                        'start': None,
                        'end': None,
                        'summary': None
                    })
                candidate['experience'] = experience
                
                candidate['education'] = []
                
                candidates.append(candidate)
                
    except Exception as e:
        print(f"Warning: Failed to parse CSV {filepath}: {e}")
        return []
    
    return candidates
