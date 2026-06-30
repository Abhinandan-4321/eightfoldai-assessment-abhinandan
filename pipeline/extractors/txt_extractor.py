import re

def extract_from_txt(filepath):
    candidates = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        candidate_blocks = content.split('---')
        
        for block in candidate_blocks:
            block = block.strip()
            if not block:
                continue
            
            candidate = {
                'source': filepath,
                'source_type': 'txt',
                'raw_data': block
            }
            
            name_match = re.search(r'(?:Candidate|Name):\s*(.+)', block, re.IGNORECASE)
            candidate['full_name'] = name_match.group(1).strip() if name_match else ''
            
            email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', block)
            candidate['emails'] = list(set(email_matches))
            
            phone_patterns = [
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            ]
            phones = []
            for pattern in phone_patterns:
                phones.extend(re.findall(pattern, block))
            candidate['phones'] = list(set(phones))
            
            location_match = re.search(r'Location:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            location_parts = {}
            if location_match:
                location_str = location_match.group(1).strip()
                parts = [p.strip() for p in location_str.split(',')]
                if len(parts) >= 1:
                    location_parts['city'] = parts[0]
                if len(parts) >= 2:
                    location_parts['region'] = parts[1]
                if len(parts) >= 3:
                    location_parts['country'] = parts[2]
            candidate['location'] = location_parts
            
            links = {}
            linkedin_match = re.search(r'(?:linkedin\.com/in/|LinkedIn:\s*)([^\s\n]+)', block, re.IGNORECASE)
            if linkedin_match:
                links['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1).strip('/')}"
            
            github_match = re.search(r'(?:github\.com/|GitHub:\s*)([^\s\n]+)', block, re.IGNORECASE)
            if github_match:
                github_user = github_match.group(1).strip('/').split('/')[-1]
                links['github'] = f"https://github.com/{github_user}"
            
            portfolio_match = re.search(r'Portfolio:\s*([^\s\n]+)', block, re.IGNORECASE)
            if portfolio_match:
                links['portfolio'] = portfolio_match.group(1).strip()
            
            candidate['links'] = links
            
            role_match = re.search(r'(?:Current Role|Title):\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
            candidate['headline'] = role_match.group(1).strip() if role_match else None
            
            years_match = re.search(r'Years of Experience:\s*(\d+)', block, re.IGNORECASE)
            if years_match:
                candidate['years_experience'] = int(years_match.group(1))
            else:
                candidate['years_experience'] = None
            
            skills_match = re.search(r'Skills?:\s*(.+?)(?:\n[A-Z]|\n\n|$)', block, re.IGNORECASE | re.DOTALL)
            if skills_match:
                skills_str = skills_match.group(1).strip()
                candidate['skills'] = [s.strip() for s in re.split(r'[,;]', skills_str) if s.strip()]
            else:
                candidate['skills'] = []
            
            experience = []
            exp_section = re.search(r'Experience:\s*(.+?)(?:\n(?:Education|Notes|GitHub|Portfolio|$))', block, re.IGNORECASE | re.DOTALL)
            if exp_section:
                exp_text = exp_section.group(1).strip()
                exp_lines = [line.strip() for line in exp_text.split('\n') if line.strip().startswith('-')]
                for line in exp_lines:
                    line = line.lstrip('- ')
                    company_match = re.match(r'(.+?)\s*\((.+?)\):\s*(.+?)(?:,\s*(.+))?$', line)
                    if company_match:
                        company = company_match.group(1).strip()
                        dates = company_match.group(2).strip()
                        title = company_match.group(3).strip()
                        summary = company_match.group(4).strip() if company_match.group(4) else None
                        
                        start, end = None, None
                        date_parts = dates.split('-')
                        if len(date_parts) == 2:
                            start = date_parts[0].strip()
                            end = date_parts[1].strip()
                        
                        experience.append({
                            'company': company,
                            'title': title,
                            'start': start,
                            'end': end,
                            'summary': summary
                        })
            candidate['experience'] = experience
            
            education = []
            edu_section = re.search(r'Education:\s*(.+?)(?:\n(?:Experience|Notes|GitHub|Portfolio|$))', block, re.IGNORECASE | re.DOTALL)
            if edu_section:
                edu_text = edu_section.group(1).strip()
                edu_lines = [line.strip() for line in edu_text.split('\n') if line.strip() and (line.strip().startswith('-') or re.search(r'\d{4}', line))]
                for line in edu_lines:
                    line = line.lstrip('- ')
                    degree_match = re.match(r'(.+?),\s*(.+?),\s*(\d{4})', line)
                    if degree_match:
                        degree = degree_match.group(1).strip()
                        institution = degree_match.group(2).strip()
                        year = int(degree_match.group(3))
                        
                        field = None
                        if ' in ' in degree:
                            parts = degree.split(' in ', 1)
                            degree = parts[0].strip()
                            field = parts[1].strip()
                        
                        education.append({
                            'institution': institution,
                            'degree': degree,
                            'field': field,
                            'end_year': year
                        })
            candidate['education'] = education
            
            candidates.append(candidate)
            
    except Exception as e:
        print(f"Warning: Failed to parse TXT {filepath}: {e}")
        return []
    
    return candidates
