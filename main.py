import argparse
import json
import sys
from pipeline.detector import detect_source_type
from pipeline.extractors.csv_extractor import extract_from_csv
from pipeline.extractors.txt_extractor import extract_from_txt
from pipeline.normalizer import normalize_candidate
from pipeline.merger import merge_candidates
from pipeline.confidence import add_confidence_scores
from pipeline.projector import project_candidates
from pipeline.validator import validate_candidates

def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def extract_candidates(filepath):
    try:
        source_type = detect_source_type(filepath)
        print(f"Detected source type: {source_type} for {filepath}")
        
        if source_type == 'csv':
            return extract_from_csv(filepath)
        elif source_type == 'txt':
            return extract_from_txt(filepath)
        else:
            print(f"Warning: Unsupported source type {source_type}")
            return []
    except Exception as e:
        print(f"Warning: Failed to extract from {filepath}: {e}")
        return []

def clean_output(candidate):
    cleaned = {}
    
    for key, value in candidate.items():
        if key in ['source', 'source_type', 'sources', 'source_types', 'raw_data']:
            continue
        
        if key == 'emails' and isinstance(value, list):
            cleaned[key] = [e['value'] if isinstance(e, dict) else e for e in value]
        elif key == 'phones' and isinstance(value, list):
            cleaned[key] = [p['value'] if isinstance(p, dict) else p for p in value]
        elif key == 'location' and isinstance(value, dict):
            loc = {k: v for k, v in value.items() if k != 'country_confidence' and v}
            cleaned[key] = loc if loc else None
        elif key == 'links' and isinstance(value, dict):
            links = {k: v for k, v in value.items() if v and (not isinstance(v, list) or len(v) > 0)}
            cleaned[key] = links if links else {}
        else:
            cleaned[key] = value
    
    return cleaned

def main():
    parser = argparse.ArgumentParser(
        description='Multi-Source Candidate Data Transformer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt
  python main.py --inputs sample_inputs/*.csv --config config/custom_config.json --output output.json
        '''
    )
    
    parser.add_argument(
        '--inputs',
        nargs='+',
        required=True,
        help='Input files (CSV, TXT, JSON)'
    )
    
    parser.add_argument(
        '--config',
        default='config/default_config.json',
        help='Output configuration file (default: config/default_config.json)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate output against canonical schema'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Multi-Source Candidate Data Transformer")
    print("=" * 60)
    
    all_candidates = []
    for filepath in args.inputs:
        print(f"\n[1/7] Extracting from: {filepath}")
        candidates = extract_candidates(filepath)
        print(f"  → Extracted {len(candidates)} candidate(s)")
        all_candidates.extend(candidates)
    
    print(f"\n[2/7] Normalizing {len(all_candidates)} candidate(s)...")
    normalized_candidates = [normalize_candidate(c) for c in all_candidates]
    print(f"  → Normalized {len(normalized_candidates)} candidate(s)")
    
    print(f"\n[3/7] Merging candidates...")
    merged_candidates = merge_candidates(normalized_candidates)
    print(f"  → Merged into {len(merged_candidates)} unique candidate(s)")
    
    print(f"\n[4/7] Calculating confidence scores...")
    scored_candidates = [add_confidence_scores(c) for c in merged_candidates]
    print(f"  → Added confidence scores")
    
    try:
        config = load_config(args.config)
        print(f"\n[5/7] Applying output config from {args.config}...")
    except:
        print(f"\n[5/7] Config file not found, using default (all fields)...")
        config = {"fields": [], "include_confidence": True, "on_missing": "null"}
    
    projected_candidates = project_candidates(scored_candidates, config)
    print(f"  → Projected {len(projected_candidates)} candidate(s)")
    
    if args.validate:
        print(f"\n[6/7] Validating output...")
        results = validate_candidates(projected_candidates)
        valid_count = sum(1 for v, _ in results if v)
        print(f"  → {valid_count}/{len(results)} candidate(s) passed validation")
    else:
        print(f"\n[6/7] Skipping validation (use --validate to enable)")
    
    print(f"\n[7/7] Cleaning and formatting output...")
    final_output = [clean_output(c) for c in projected_candidates]
    
    output_json = json.dumps(final_output, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"  → Output written to {args.output}")
    else:
        print("\n" + "=" * 60)
        print("OUTPUT:")
        print("=" * 60)
        print(output_json)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
