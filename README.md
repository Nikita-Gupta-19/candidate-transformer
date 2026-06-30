# Candidate Data Transformer

A robust, deterministic data pipeline that ingests candidate data from heterogeneous sources (structured and unstructured), normalizes it, merges duplicates into a single canonical profile, tracks data provenance and confidence, and dynamically projects the final profile based on runtime configuration.

## Features
- **Deterministic IDs**: Generates SHA256 deterministic identifiers based on primary emails or phones.
- **Normalization**: Standardizes fields like E.164 phone numbers and canonical skills.
- **Provenance & Confidence**: Tracks the source, extraction method, and calculated confidence for every scalar value and array element.
- **Merging**: Groups candidate records deterministically based on overlapping identity keys (emails/phones). Resolves conflicts using a strict policy: highest confidence -> source priority -> lexicographical fallback.
- **Configurable Output**: Dynamically projects internal schemas into customized JSON outputs based on a runtime JSON configuration.
- **Validation**: Ensures schema compliance both internally and post-projection. Gracefully drops invalid fields (e.g. malformed emails) with logging instead of crashing.

## Getting Started

### Prerequisites
- Python 3.9+

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage
Run the pipeline using the CLI tool. You can supply multiple inputs.

```bash
python main.py \
    --csv inputs/candidate.csv \
    --resume inputs/resume.txt \
    --config config/custom.json \
    --output custom_output.json
```

If you do not specify a `--config`, it will output the full canonical schema (with full provenance metadata) by default.

### Tests
To run the unit tests:
```bash
PYTHONPATH=. pytest tests/
```

## Architecture

```text
candidate-transformer/
├── main.py                 # CLI entry point
├── config/                 # Default and custom projection configs
├── src/
│   ├── models.py           # Pydantic internal canonical schemas
│   ├── parsers/            # Extraction from CSV and unstructured Resumes
│   ├── normalizers/        # Phone, skill, and date standardization
│   ├── merger/             # Deterministic matching and conflict resolution
│   ├── projection/         # Config-driven schema projection logic
│   └── validators/         # Post-extraction and post-projection validation
└── tests/                  # Pytest unit tests
```
