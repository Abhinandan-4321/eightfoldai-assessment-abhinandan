import jsonschema

CANONICAL_SCHEMA = {
    "type": "object",
    "properties": {
        "candidate_id": {"type": "string"},
        "full_name": {"type": "string"},
        "emails": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                ]
            }
        },
        "phones": {
            "type": "array",
            "items": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                ]
            }
        },
        "location": {
            "type": "object",
            "properties": {
                "city": {"type": ["string", "null"]},
                "region": {"type": ["string", "null"]},
                "country": {"type": ["string", "null"]},
                "country_confidence": {"type": "number"}
            }
        },
        "links": {
            "type": "object",
            "properties": {
                "linkedin": {"type": ["string", "null"]},
                "github": {"type": ["string", "null"]},
                "portfolio": {"type": ["string", "null"]},
                "other": {"type": "array", "items": {"type": "string"}}
            }
        },
        "headline": {"type": ["string", "null"]},
        "years_experience": {"type": ["number", "null"]},
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "confidence": {"type": "number"},
                    "sources": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "title": {"type": "string"},
                    "start": {"type": ["string", "null"]},
                    "end": {"type": ["string", "null"]},
                    "summary": {"type": ["string", "null"]}
                }
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": ["string", "null"]},
                    "end_year": {"type": "integer"}
                }
            }
        },
        "provenance": {"type": "object"},
        "overall_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    }
}

def validate_candidate(candidate, schema=None):
    if schema is None:
        schema = CANONICAL_SCHEMA
    
    try:
        jsonschema.validate(instance=candidate, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, str(e)

def validate_candidates(candidates, schema=None):
    results = []
    for i, candidate in enumerate(candidates):
        valid, error = validate_candidate(candidate, schema)
        if not valid:
            print(f"Warning: Candidate {i} validation failed: {error}")
        results.append((valid, error))
    return results
