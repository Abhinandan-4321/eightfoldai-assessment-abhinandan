import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.extractors.csv_extractor import extract_from_csv
from pipeline.extractors.txt_extractor import extract_from_txt
from pipeline.normalizer import normalize_candidate
from pipeline.merger import merge_candidates
from pipeline.confidence import add_confidence_scores

def test_end_to_end_pipeline():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'sample_inputs', 'recruiter_export.csv')
    txt_path = os.path.join(os.path.dirname(__file__), '..', 'sample_inputs', 'recruiter_notes.txt')
    
    print("Testing end-to-end pipeline...")
    
    csv_candidates = extract_from_csv(csv_path)
    print(f"  → Extracted {len(csv_candidates)} candidates from CSV")
    assert len(csv_candidates) > 0
    
    txt_candidates = extract_from_txt(txt_path)
    print(f"  → Extracted {len(txt_candidates)} candidates from TXT")
    assert len(txt_candidates) > 0
    
    all_candidates = csv_candidates + txt_candidates
    print(f"  → Total candidates: {len(all_candidates)}")
    
    normalized = [normalize_candidate(c) for c in all_candidates]
    print(f"  → Normalized {len(normalized)} candidates")
    assert len(normalized) == len(all_candidates)
    
    merged = merge_candidates(normalized)
    print(f"  → Merged into {len(merged)} unique candidates")
    assert len(merged) < len(all_candidates)
    
    scored = [add_confidence_scores(c) for c in merged]
    print(f"  → Added confidence scores")
    assert all('overall_confidence' in c for c in scored)
    assert all('provenance' in c for c in scored)
    
    print("✓ End-to-end pipeline test passed")
    
    for i, candidate in enumerate(scored):
        print(f"\nCandidate {i+1}:")
        print(f"  Name: {candidate.get('full_name')}")
        print(f"  Emails: {[e['value'] if isinstance(e, dict) else e for e in candidate.get('emails', [])]}")
        print(f"  Overall Confidence: {candidate.get('overall_confidence')}")

if __name__ == '__main__':
    test_end_to_end_pipeline()
    print("\n✅ End-to-end pipeline test passed!")
