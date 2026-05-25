# Data

Two subdirectories:

- `raw/` - exactly what came back from data.ny.gov. Not committed
  (see .gitignore). Re-run `scripts/fetch_ridership.py` to populate.
- `clean/` - what the cleaning scripts produce. Committed so the
  dashboard works without re-running the pipeline.
