# Eightfold Multi-Source Candidate Data Transformer — Technical Design

**Author**: [Your Name] | **Email**: [Your Email]

---

## 1. Pipeline Architecture

The system follows a **7-stage pipeline** that transforms messy, multi-source candidate data into a clean, canonical profile:

```
┌─────────┐   ┌─────────┐   ┌───────────┐   ┌───────┐   ┌────────────┐   ┌─────────┐   ┌──────────┐
│ Detect  │ → │ Extract │ → │ Normalize │ → │ Merge │ → │ Confidence │ → │ Project │ → │ Validate │
└─────────┘   └─────────┘   └───────────┘   └───────┘   └────────────┘   └─────────┘   └──────────┘
```

### Stage Descriptions

1. **Detect** — Identify source type (CSV, TXT) from file extension and content sniffing.
2. **Extract** — Parse each source into intermediate representation (list of raw candidate dicts).
3. **Normalize** — Standardize formats: E.164 phones, ISO-3166 countries, YYYY-MM dates, canonical skill names.
4. **Merge** — Match candidates across sources using email/name keys; resolve conflicts via priority rules; deduplicate.
5. **Confidence** — Score each field (0.0–1.0) based on source reliability and cross-source agreement.
6. **Project** — Apply runtime output config (field selection, renaming, normalization toggles).
7. **Validate** — Check final JSON against schema; degrade gracefully on invalid data.

---

## 2. Canonical Output Schema

| Field | Type | Normalization | Notes |
|-------|------|---------------|-------|
| `candidate_id` | `string` | SHA256 hash | Deterministic from name+email |
| `full_name` | `string` | Title case | |
| `emails` | `string[]` | Lowercase | Deduplicated |
| `phones` | `string[]` | **E.164** | e.g., `+14155552671` |
| `location` | `{city, region, country}` | **ISO-3166 alpha-2** | country: `US`, `IN`, etc. |
| `links` | `{linkedin, github, portfolio, other[]}` | URLs | |
| `headline` | `string \| null` | — | Job title or tagline |
| `years_experience` | `number \| null` | — | Computed or extracted |
| `skills` | `[{name, confidence, sources[]}]` | **Canonical names** | e.g., `JavaScript` not `js` |
| `experience` | `[{company, title, start, end, summary}]` | **YYYY-MM dates** | Chronological order |
| `education` | `[{institution, degree, field, end_year}]` | — | |
| `provenance` | `{field → {source, method, confidence}}` | — | Per-field tracking |
| `overall_confidence` | `number` | 0.0–1.0 | Weighted average of field confidences |

### Normalization Examples
- **Phone**: `(415) 555-2671` → `+14155552671` (E.164)
- **Country**: `United States` → `US` (ISO-3166)
- **Date**: `Jan 2020` → `2020-01` (YYYY-MM)
- **Skill**: `react.js` → `React` (canonical)

---

## 3. Merge & Conflict Resolution Policy

### Matching Strategy
Candidates are matched across sources using:
- **Primary key**: Normalized email (exact match)
- **Fallback key**: Normalized full name + any phone number overlap

### Priority Rules
When values conflict:
1. **Source priority**: Structured (CSV) > Unstructured (TXT)
2. **Non-null preference**: Prefer non-null over null
3. **Multi-source boost**: Values confirmed by multiple sources get higher confidence

### Field-Specific Rules
- **Lists** (emails, phones, skills): Union + deduplicate
- **Scalars** (name, headline): Use highest-priority source
- **Arrays of objects** (experience, education): Merge + deduplicate by key fields

### Confidence Assignment
```
Base confidence:
- CSV (structured): 0.85
- TXT (unstructured): 0.60

Adjustments:
- Multi-source agreement: +0.15
- Heuristic extraction: -0.20
- Malformed data: -0.30
```

---

## 4. Runtime Custom-Output Config

A **JSON config file** controls output shape without code changes:

```json
{
  "fields": [
    {"path": "full_name", "type": "string", "required": true},
    {"path": "primary_email", "from": "emails[0]", "type": "string", "required": true},
    {"path": "phone", "from": "phones[0]", "type": "string", "normalize": "E164"},
    {"path": "skills", "from": "skills[].name", "type": "string[]", "normalize": "canonical"}
  ],
  "include_confidence": true,
  "on_missing": "null"
}
```

### Config Capabilities
- **Field selection**: Include only specified fields
- **Renaming**: `"primary_email"` from `"emails[0]"`
- **Path expressions**: Array indexing, nested object access
- **Per-field normalization**: Toggle E.164, canonical, etc.
- **Missing-value policy**: `null`, `omit`, or `error`
- **Provenance toggle**: Include/exclude per-field tracking

---

## 5. Edge Cases & Design Decisions

### Handled Edge Cases

1. **Garbage/Missing Source**
   - **Scenario**: File not found, unparseable CSV, corrupt data
   - **Handling**: Log warning, skip source, continue with remaining sources
   - **Rationale**: Partial data is better than no data

2. **Conflicting Values**
   - **Scenario**: CSV says name is "John Smith", TXT says "Jon Smith"
   - **Handling**: Use priority rules (CSV wins); log conflict in provenance
   - **Rationale**: Structured sources are more reliable

3. **Empty/Null Fields**
   - **Scenario**: CSV has no phone number for a candidate
   - **Handling**: Output `null`, never invent data
   - **Rationale**: Honesty over completeness

4. **Malformed Data**
   - **Scenario**: Phone number is `"123"` or `"N/A"`
   - **Handling**: Best-effort parse; if unparseable, keep raw with low confidence (0.3)
   - **Rationale**: Preserve information for manual review

5. **Cross-Source Duplicates**
   - **Scenario**: Same candidate in CSV and TXT
   - **Handling**: Merge into single record using match keys
   - **Rationale**: Avoid duplicate profiles in output

### Deliberately Out-of-Scope (Time Constraints)

- **Fuzzy name matching**: No Levenshtein distance (exact match only)
- **External API calls**: No LinkedIn/GitHub scraping (privacy + rate limits)
- **ML-based extraction**: No NLP models for unstructured text (heuristics only)
- **Historical versioning**: No audit trail of profile changes over time

---

## Summary

This design prioritizes **robustness** (graceful degradation), **transparency** (provenance tracking), and **flexibility** (runtime config) over feature completeness. The pipeline is deterministic, testable, and scales to thousands of candidates.
