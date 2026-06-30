# Quick Start Guide

Get the pipeline running in 3 minutes.

## Step 1: Install Dependencies (30 seconds)

```bash
cd d:\eightfoldai-round2
pip install -r requirements.txt
```

## Step 2: Run the Pipeline (30 seconds)

### Default Output (All Fields + Provenance)
```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --output sample_outputs/default_output.json
```

**Expected**: 9 candidates → 7 unique (Alice and Bob merged from both sources)

### Custom Output (Selected Fields Only)
```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --config config/custom_config.json --output sample_outputs/custom_output.json
```

**Expected**: Same 7 candidates, but only selected fields (no provenance)

## Step 3: View Results (30 seconds)

### Windows
```powershell
cat sample_outputs/default_output.json
cat sample_outputs/custom_output.json
```

### Linux/Mac
```bash
cat sample_outputs/default_output.json
cat sample_outputs/custom_output.json
```

## Step 4: Run Tests (30 seconds)

```bash
python tests/test_normalizer.py
python tests/test_merger.py
python tests/test_pipeline.py
```

**Expected**: All tests pass ✅

## What to Look For

### In default_output.json
- ✅ 7 candidates (Alice, Bob, Carol, David, Emma, Frank, Grace)
- ✅ Alice has 6 skills merged from CSV + TXT sources
- ✅ Phones in E.164 format: `+14155550123`
- ✅ Country codes: `US` (ISO-3166)
- ✅ Provenance shows which source each field came from
- ✅ Overall confidence: 0.72–0.94

### In custom_output.json
- ✅ Same 7 candidates
- ✅ Only selected fields: candidate_id, full_name, primary_email, phone, city, country, skills, years_experience, headline
- ✅ No provenance or overall_confidence
- ✅ Skills as simple array: `["Python", "React", "AWS"]`

## Common Issues

### ModuleNotFoundError: No module named 'phonenumbers'
**Solution**: Run `pip install -r requirements.txt`

### FileNotFoundError: sample_outputs/
**Solution**: Run `mkdir sample_outputs`

### No output displayed
**Solution**: Remove `--output` flag to print to stdout:
```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt
```

## Next Steps

- Read `DESIGN.md` for technical design details
- Read `README.md` for full documentation
- Read `TESTING_GUIDE.md` for comprehensive testing instructions
- Read `IMPLEMENTATION_SUMMARY.md` for project overview
