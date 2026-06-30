import re
import phonenumbers
import pycountry

SKILL_CANONICAL_MAP = {
    'js': 'JavaScript',
    'javascript': 'JavaScript',
    'react.js': 'React',
    'reactjs': 'React',
    'react': 'React',
    'vue.js': 'Vue.js',
    'vuejs': 'Vue.js',
    'vue': 'Vue.js',
    'python': 'Python',
    'py': 'Python',
    'java': 'Java',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'node.js': 'Node.js',
    'nodejs': 'Node.js',
    'node': 'Node.js',
    'aws': 'AWS',
    'amazon web services': 'AWS',
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'k8s': 'Kubernetes',
    'sql': 'SQL',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'mysql': 'MySQL',
    'mongodb': 'MongoDB',
    'mongo': 'MongoDB',
    'machine learning': 'Machine Learning',
    'ml': 'Machine Learning',
    'deep learning': 'Deep Learning',
    'tensorflow': 'TensorFlow',
    'pytorch': 'PyTorch',
    'scikit-learn': 'Scikit-learn',
    'sklearn': 'Scikit-learn',
    'pandas': 'Pandas',
    'numpy': 'NumPy',
    'html': 'HTML',
    'css': 'CSS',
    'figma': 'Figma',
    'sketch': 'Sketch',
    'terraform': 'Terraform',
    'git': 'Git',
    'github': 'GitHub',
    'agile': 'Agile',
    'scrum': 'Scrum',
}

COUNTRY_NAME_MAP = {
    'united states': 'US',
    'usa': 'US',
    'us': 'US',
    'united states of america': 'US',
    'india': 'IN',
    'united kingdom': 'GB',
    'uk': 'GB',
    'canada': 'CA',
    'australia': 'AU',
    'germany': 'DE',
    'france': 'FR',
    'china': 'CN',
    'japan': 'JP',
}

def normalize_phone(phone_str):
    if not phone_str or phone_str.lower() in ['n/a', 'none', '']:
        return None, 0.0
    
    try:
        parsed = phonenumbers.parse(phone_str, "US")
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), 0.9
        else:
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), 0.6
    except Exception:
        cleaned = re.sub(r'[^\d+]', '', phone_str)
        if len(cleaned) >= 10:
            return f"+1{cleaned[-10:]}" if not cleaned.startswith('+') else cleaned, 0.3
        return phone_str, 0.2

def normalize_email(email_str):
    if not email_str:
        return None, 0.0
    
    email_str = email_str.lower().strip()
    if re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email_str):
        return email_str, 0.95
    return email_str, 0.5

def normalize_country(country_str):
    if not country_str:
        return None, 0.0
    
    country_str = country_str.strip().lower()
    
    if country_str in COUNTRY_NAME_MAP:
        return COUNTRY_NAME_MAP[country_str], 0.9
    
    try:
        country = pycountry.countries.search_fuzzy(country_str)[0]
        return country.alpha_2, 0.85
    except Exception:
        return country_str, 0.3

def normalize_skill(skill_str):
    if not skill_str:
        return None, 0.0
    
    skill_lower = skill_str.strip().lower()
    if skill_lower in SKILL_CANONICAL_MAP:
        return SKILL_CANONICAL_MAP[skill_lower], 0.9
    
    return skill_str.strip().title(), 0.7

def normalize_date(date_str):
    if not date_str or date_str.lower() in ['present', 'current', 'now']:
        return 'present', 0.9
    
    date_str = str(date_str).strip()
    
    yyyy_mm_match = re.match(r'^(\d{4})-(\d{2})$', date_str)
    if yyyy_mm_match:
        return date_str, 0.95
    
    month_year_match = re.match(r'^([A-Za-z]+)\s+(\d{4})$', date_str)
    if month_year_match:
        month_name = month_year_match.group(1)
        year = month_year_match.group(2)
        month_map = {
            'jan': '01', 'january': '01',
            'feb': '02', 'february': '02',
            'mar': '03', 'march': '03',
            'apr': '04', 'april': '04',
            'may': '05',
            'jun': '06', 'june': '06',
            'jul': '07', 'july': '07',
            'aug': '08', 'august': '08',
            'sep': '09', 'september': '09',
            'oct': '10', 'october': '10',
            'nov': '11', 'november': '11',
            'dec': '12', 'december': '12',
        }
        month_num = month_map.get(month_name.lower())
        if month_num:
            return f"{year}-{month_num}", 0.85
    
    year_only_match = re.match(r'^(\d{4})$', date_str)
    if year_only_match:
        return f"{date_str}-01", 0.7
    
    return date_str, 0.4

def normalize_candidate(candidate):
    normalized = candidate.copy()
    
    if candidate.get('full_name'):
        normalized['full_name'] = candidate['full_name'].strip().title()
    
    normalized_emails = []
    for email in candidate.get('emails', []):
        norm_email, conf = normalize_email(email)
        if norm_email:
            normalized_emails.append({'value': norm_email, 'confidence': conf})
    normalized['emails'] = normalized_emails
    
    normalized_phones = []
    for phone in candidate.get('phones', []):
        norm_phone, conf = normalize_phone(phone)
        if norm_phone:
            normalized_phones.append({'value': norm_phone, 'confidence': conf})
    normalized['phones'] = normalized_phones
    
    if candidate.get('location'):
        location = candidate['location'].copy()
        if location.get('country'):
            norm_country, conf = normalize_country(location['country'])
            location['country'] = norm_country
            location['country_confidence'] = conf
        normalized['location'] = location
    
    normalized_skills = []
    for skill in candidate.get('skills', []):
        norm_skill, conf = normalize_skill(skill)
        if norm_skill:
            normalized_skills.append({'name': norm_skill, 'confidence': conf, 'sources': [candidate['source']]})
    normalized['skills'] = normalized_skills
    
    normalized_experience = []
    for exp in candidate.get('experience', []):
        norm_exp = exp.copy()
        if exp.get('start'):
            norm_exp['start'], _ = normalize_date(exp['start'])
        if exp.get('end'):
            norm_exp['end'], _ = normalize_date(exp['end'])
        normalized_experience.append(norm_exp)
    normalized['experience'] = normalized_experience
    
    return normalized
