import os

def detect_source_type(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.csv':
        return 'csv'
    elif ext == '.txt':
        return 'txt'
    elif ext == '.json':
        return 'json'
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024)
            if content.strip().startswith('{') or content.strip().startswith('['):
                return 'json'
            elif ',' in content and '\n' in content:
                return 'csv'
            else:
                return 'txt'
