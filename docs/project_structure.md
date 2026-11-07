# Repository structure

```text
src/sea_it_jobs/       # Python code: source, parser, files, and Job commands
notebooks/            # Databricks entry points
dbt/                  # SQL models, mappings, and data tests
infra/terraform/      # Workspace setup
dashboards/           # Dashboard template
scripts/              # Deployment and setup helpers
tests/                # Python and SQL tests
docs/                 # Project notes and instructions
.github/workflows/    # CI and daily schedule
```

Inside `dbt/`:

- `models/staging/`: read Bronze and set types.
- `models/intermediate/`: choose current records and normalize skills/cities.
- `models/marts/`: build fact, dimension, bridge, and report tables.
- `seeds/`: city and skill aliases.
- `tests/`: data checks.

`pyproject.toml` lists Python dependencies; `uv.lock` pins them. `.terraform.lock.hcl` pins the provider. Local raw files, logs, plans, `.env`, and Terraform state are excluded from Git.
