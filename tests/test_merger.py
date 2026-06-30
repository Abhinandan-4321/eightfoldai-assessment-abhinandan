import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.merger import candidates_match, merge_two_candidates, merge_candidates

def test_candidates_match():
    cand1 = {
        'full_name': 'Alice Johnson',
        'emails': [{'value': 'alice@email.com'}],
        'phones': [{'value': '+14155550123'}]
    }
    
    cand2 = {
        'full_name': 'Alice Johnson',
        'emails': [{'value': 'alice@email.com'}],
        'phones': [{'value': '+14155550123'}]
    }
    
    assert candidates_match(cand1, cand2) == True
    print("✓ Candidate matching test passed")

def test_merge_two_candidates():
    cand1 = {
        'source': 'file1.csv',
        'source_type': 'csv',
        'full_name': 'Alice Johnson',
        'emails': [{'value': 'alice@email.com'}],
        'phones': [{'value': '+14155550123'}],
        'location': {'city': 'San Francisco', 'region': 'CA', 'country': 'US'},
        'skills': [{'name': 'Python', 'confidence': 0.85, 'sources': ['file1.csv']}],
        'experience': [],
        'education': [],
        'links': {}
    }
    
    cand2 = {
        'source': 'file2.txt',
        'source_type': 'txt',
        'full_name': 'Alice Johnson',
        'emails': [{'value': 'alice@email.com'}],
        'phones': [{'value': '+14155550123'}],
        'location': {'city': 'San Francisco', 'region': 'CA', 'country': 'US'},
        'skills': [{'name': 'React', 'confidence': 0.60, 'sources': ['file2.txt']}],
        'experience': [],
        'education': [],
        'links': {}
    }
    
    merged = merge_two_candidates(cand1, cand2)
    
    assert merged['full_name'] == 'Alice Johnson'
    assert len(merged['skills']) == 2
    assert merged['sources'] == ['file1.csv', 'file2.txt']
    print("✓ Merge two candidates test passed")

def test_merge_candidates_dedup():
    candidates = [
        {
            'source': 'file1.csv',
            'source_type': 'csv',
            'full_name': 'Alice Johnson',
            'emails': [{'value': 'alice@email.com'}],
            'phones': [{'value': '+14155550123'}],
            'location': {},
            'skills': [],
            'experience': [],
            'education': [],
            'links': {}
        },
        {
            'source': 'file2.txt',
            'source_type': 'txt',
            'full_name': 'Alice Johnson',
            'emails': [{'value': 'alice@email.com'}],
            'phones': [{'value': '+14155550123'}],
            'location': {},
            'skills': [],
            'experience': [],
            'education': [],
            'links': {}
        },
        {
            'source': 'file1.csv',
            'source_type': 'csv',
            'full_name': 'Bob Smith',
            'emails': [{'value': 'bob@email.com'}],
            'phones': [{'value': '+16505550198'}],
            'location': {},
            'skills': [],
            'experience': [],
            'education': [],
            'links': {}
        }
    ]
    
    merged = merge_candidates(candidates)
    
    assert len(merged) == 2
    print("✓ Merge candidates deduplication test passed")

if __name__ == '__main__':
    test_candidates_match()
    test_merge_two_candidates()
    test_merge_candidates_dedup()
    print("\n✅ All merger tests passed!")
