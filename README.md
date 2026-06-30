# Eightfold Multi-Source Candidate Data Transformer

A Python CLI pipeline that transforms messy, multi-source candidate data into clean, canonical profiles with confidence scores and provenance tracking.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Pipeline

**Default output** (all fields + provenance):
```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --output sample_outputs/default_output.json
```

**Custom output** (selected fields only):
```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --config config/custom_config.json --output sample_outputs/custom_output.json
```

### 3. Run Tests
```bash
python tests/test_normalizer.py
python tests/test_merger.py
python tests/test_pipeline.py
```

**Expected**: All tests pass ✅ (9 input candidates → 7 unique output candidates)

## What It Does

**Input**: Messy candidate data from multiple sources (CSV + TXT files)
**Output**: Clean, deduplicated JSON with confidence scores

**Pipeline**: Detect → Extract → Normalize → Merge → Confidence → Project → Validate

**Key Features**:
- Merges duplicates across sources (9 input → 7 unique output)
- Normalizes formats: E.164 phones, ISO-3166 countries, YYYY-MM dates
- Confidence scoring: 0.0–1.0 per field based on source reliability
- Provenance tracking: Shows which source each field came from
- Runtime config: Change output fields without code changes

## Output Schema (13 Fields)

`candidate_id`, `full_name`, `emails[]`, `phones[]` (E.164), `location` {city, region, country (ISO-3166)}, `links`, `headline`, `years_experience`, `skills[]` {name, confidence, sources[]}, `experience[]`, `education[]`, `provenance`, `overall_confidence` (0.0–1.0)

## Project Structure

```
├── main.py                      # CLI entry point
├── pipeline/                    # 7-stage pipeline modules
│   ├── detector.py
│   ├── extractors/ (csv, txt)
│   ├── normalizer.py
│   ├── merger.py
│   ├── confidence.py
│   ├── projector.py
│   └── validator.py
├── config/                      # Output configurations
├── sample_inputs/               # CSV + TXT sample data
├── sample_outputs/              # Generated outputs
└── tests/                       # Unit + integration tests
```

## Requirements

- Python 3.7+
- Dependencies: `phonenumbers`, `pycountry`, `jsonschema` (see `requirements.txt`)
