# Eightfold Candidate Data Transformer — Design

### Pipeline (7 Stages)
Detect → Extract → Normalize → Merge → Confidence → Project → Validate
- **Detect**: File type (CSV/TXT) | **Extract**: Parse to dict | **Normalize**: E.164 phones, ISO-3166 countries, YYYY-MM dates, canonical skills
- **Merge**: Match by email/name, priority rules (CSV>TXT), deduplicate | **Confidence**: Score 0.0–1.0 per field
- **Project**: Runtime JSON config (field selection, renaming) | **Validate**: Schema check, graceful degradation

### Output Schema (13 Fields)
candidate_id (SHA256), full_name, emails[], phones[] (E.164), location {city, region, country (ISO-3166)}, links {linkedin, github, portfolio}, headline, years_experience, skills [{name, confidence, sources[]}], experience [{company, title, start (YYYY-MM), end, summary}], education [{institution, degree, field, end_year}], provenance {field→{source, method, confidence}}, overall_confidence (0.0–1.0)

### Merge Policy
**Match**: Email (exact) OR name + phone overlap | **Priority**: CSV (0.85) > TXT (0.60) | **Lists**: Union+deduplicate | **Scalars**: Higher priority | **Multi-source**: +0.15 confidence boost

### Runtime Config
```json
{"fields": [{"path": "full_name", "required": true}, {"path": "primary_email", "from": "emails[0]"}],
 "include_confidence": false, "on_missing": "null"}
```
Supports: field selection, renaming, path expressions (skills[].name), per-field normalization, missing-value policy

### Edge Cases
1. Garbage/missing source → log, skip, continue | 2. Conflicting values → priority rules, log in provenance
3. Empty fields → null (never invent) | 4. Malformed data → best-effort parse, low confidence (0.3)
5. Cross-source duplicates → merge into one record

### Design Principles
**Deterministic**: Same inputs→same outputs | **Robust**: Handles bad input gracefully | **Transparent**: Provenance+confidence tracking | **Flexible**: Runtime config, no code changes | **Scalable**: Thousands of candidates

### Out-of-Scope
No fuzzy matching, no external APIs, no ML extraction, no versioning
