# Testing Guide

This document provides step-by-step instructions to test the Multi-Source Candidate Data Transformer.

## Prerequisites

1. **Install Python 3.7+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Test 1: Unit Tests

### Normalizer Tests
Tests phone, email, country, skill, and date normalization.

```bash
python tests/test_normalizer.py
```

**Expected output:**
```
✓ Phone normalization tests passed
✓ Email normalization tests passed
✓ Country normalization tests passed
✓ Skill normalization tests passed
✓ Date normalization tests passed

✅ All normalizer tests passed!
```

### Merger Tests
Tests candidate matching, merging, and deduplication.

```bash
python tests/test_merger.py
```

**Expected output:**
```
✓ Candidate matching test passed
✓ Merge two candidates test passed
✓ Merge candidates deduplication test passed

✅ All merger tests passed!
```

### End-to-End Pipeline Test
Tests the complete pipeline with sample data.

```bash
python tests/test_pipeline.py
```

**Expected output:**
```
Testing end-to-end pipeline...
  → Extracted 5 candidates from CSV
  → Extracted 4 candidates from TXT
  → Total candidates: 9
  → Normalized 9 candidates
  → Merged into 7 unique candidates
  → Added confidence scores
✓ End-to-end pipeline test passed

Candidate 1:
  Name: Alice Johnson
  Emails: ['alice.johnson@email.com']
  Overall Confidence: 0.94
...

✅ End-to-end pipeline test passed!
```

## Test 2: Default Output (All Fields)

Run the pipeline with default configuration (includes all fields, provenance, and confidence scores).

```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --output sample_outputs/default_output.json
```

**Expected output:**
```
============================================================
Multi-Source Candidate Data Transformer
============================================================

[1/7] Extracting from: sample_inputs/recruiter_export.csv
Detected source type: csv for sample_inputs/recruiter_export.csv
  → Extracted 5 candidate(s)

[1/7] Extracting from: sample_inputs/recruiter_notes.txt
Detected source type: txt for sample_inputs/recruiter_notes.txt
  → Extracted 4 candidate(s)

[2/7] Normalizing 9 candidate(s)...
  → Normalized 9 candidate(s)

[3/7] Merging candidates...
  → Merged into 7 unique candidate(s)

[4/7] Calculating confidence scores...
  → Added confidence scores

[5/7] Applying output config from config/default_config.json...
  → Projected 7 candidate(s)

[6/7] Skipping validation (use --validate to enable)

[7/7] Cleaning and formatting output...
  → Output written to sample_outputs/default_output.json

============================================================
Pipeline completed successfully!
============================================================
```

**Verify output:**
```bash
# View the output file
cat sample_outputs/default_output.json
```

**What to check:**
- 7 unique candidates (Alice, Bob, Carol, David, Emma, Frank, Grace)
- Alice and Bob appear in both sources → merged with higher confidence
- All fields present: candidate_id, full_name, emails, phones, location, links, headline, years_experience, skills, experience, education, provenance, overall_confidence
- Phones in E.164 format (e.g., `+14155550123`)
- Country codes in ISO-3166 (e.g., `US`)
- Skills have confidence scores and source tracking

## Test 3: Custom Output (Selected Fields)

Run the pipeline with custom configuration (selected fields only, no provenance).

```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --config config/custom_config.json --output sample_outputs/custom_output.json
```

**Expected output:**
```
============================================================
Multi-Source Candidate Data Transformer
============================================================
...
[5/7] Applying output config from config/custom_config.json...
  → Projected 7 candidate(s)
...
  → Output written to sample_outputs/custom_output.json

============================================================
Pipeline completed successfully!
============================================================
```

**Verify output:**
```bash
cat sample_outputs/custom_output.json
```

**What to check:**
- Only selected fields: candidate_id, full_name, primary_email, phone, city, country, skills, years_experience, headline
- No provenance or overall_confidence fields
- `primary_email` is extracted from `emails[0]`
- `skills` is an array of skill names (not objects)

## Test 4: Edge Cases

### Test 4.1: Missing Source File
```bash
python main.py --inputs nonexistent.csv sample_inputs/recruiter_notes.txt
```

**Expected:** Warning logged, continues with remaining sources, doesn't crash.

### Test 4.2: Empty CSV
Create an empty CSV file:
```bash
echo "name,email,phone" > test_empty.csv
python main.py --inputs test_empty.csv
```

**Expected:** Extracts 0 candidates, completes successfully.

### Test 4.3: Malformed Phone Number
The sample data includes various phone formats:
- `(415) 555-0123` → normalized to `+14155550123`
- `+1-650-555-0198` → normalized to `+16505550198`
- `4085550167` → normalized to `+14085550167`

**Verify:** All phones in output are E.164 format.

### Test 4.4: Duplicate Candidates
Alice Johnson appears in both CSV and TXT sources.

**Verify:** 
- Only one Alice Johnson in output
- Her skills are merged from both sources
- Skills from both sources have higher confidence (0.95 vs 0.9)
- Provenance shows both sources

## Test 5: Validation

Run with validation enabled:

```bash
python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --validate
```

**Expected output:**
```
[6/7] Validating output...
  → 7/7 candidate(s) passed validation
```

## Test 6: Design Decisions Verification

### Merge Priority (CSV > TXT)
Alice Johnson has:
- CSV: `years_experience: 8`
- TXT: No years_experience field

**Verify:** Output shows `years_experience: 8.0` (from CSV, higher priority).

### Multi-Source Confidence Boost
Alice's Python skill appears in both sources.

**Verify:** 
- Python skill has confidence 0.95 (boosted from base 0.85/0.60)
- Sources array shows both files

### Canonical Skill Names
CSV has `"Python, JavaScript, React, AWS"`.

**Verify:** All skills are properly capitalized and canonical (e.g., `JavaScript` not `javascript`).

### Country Normalization
TXT has `"United States"` and `"USA"`.

**Verify:** Both normalized to `"US"` (ISO-3166 alpha-2).

## Summary of Test Results

If all tests pass, you should see:
- ✅ All unit tests pass (normalizer, merger, pipeline)
- ✅ Default output contains 7 candidates with full schema
- ✅ Custom output contains 7 candidates with selected fields only
- ✅ Edge cases handled gracefully (missing files, empty data, malformed input)
- ✅ Validation passes for all candidates
- ✅ Merge logic works correctly (deduplication, priority, confidence boost)
- ✅ Normalization works correctly (E.164 phones, ISO-3166 countries, canonical skills)

## Demo Video Script

For the 2-minute demo video, follow this script:

1. **[0:00-0:15] Introduction**
   - "This is the Multi-Source Candidate Data Transformer"
   - Show project structure in file explorer

2. **[0:15-0:45] Run with default config**
   - Run: `python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --output sample_outputs/default_output.json`
   - Show console output (7-stage pipeline)
   - Open `default_output.json` and highlight:
     - Alice Johnson merged from both sources
     - Skills with confidence scores
     - Provenance tracking

3. **[0:45-1:15] Run with custom config**
   - Show `config/custom_config.json` (selected fields only)
   - Run: `python main.py --inputs sample_inputs/recruiter_export.csv sample_inputs/recruiter_notes.txt --config config/custom_config.json --output sample_outputs/custom_output.json`
   - Open `custom_output.json` and highlight:
     - Only selected fields
     - No provenance
     - Skills as simple array

4. **[1:15-1:45] Show design decisions**
   - Open `DESIGN.md` and highlight:
     - Pipeline architecture diagram
     - Merge policy (CSV > TXT priority)
     - Edge cases handled

5. **[1:45-2:00] Conclusion**
   - "The pipeline is deterministic, testable, and handles real-world edge cases gracefully"
   - Show test results: `python tests/test_pipeline.py`
