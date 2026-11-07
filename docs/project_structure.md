# Repository structure

```text
sea-it-jobs-pipeline/
├── src/sea_it_jobs/       # CLI, HTTP, real-source adapter, parser, ingestion, and SDK
│   └── sources/          # Verified ITviec adapter
├── notebooks/            # Databricks extraction and PySpark Bronze entry points
├── dbt/
│   ├── models/staging/   # Bronze contracts, types, FX, and observation history
│   ├── models/intermediate/ # Current records and skill/city normalization
│   ├── models/marts/     # Dimensions, facts, bridges, and reports
│   ├── macros/           # Schema naming and surrogate keys
│   ├── seeds/            # Controlled alias mappings
│   └── tests/            # Cloud SQL business/data checks
├── infra/terraform/      # Workspace resources and provider lock
├── dashboards/           # Deployed AI/BI dashboard template
├── scripts/              # Dashboard generation and Terraform/GitHub configuration
├── tests/                # Unit, raw-integrity, and SQL semantic tests
├── docs/                 # Architecture, contracts, dictionary, operations, and learning
├── .github/workflows/    # CI and scheduled Databricks Job submission/waiting
├── artifacts/            # Real raw files, logs, plans, and tools; excluded from Git
├── .env                  # Private local configuration; excluded from Git
├── pyproject.toml
├── uv.lock
└── Makefile
```

Source extraction, uploads, and transformations have separate responsibilities rather than being combined into one script. Notebooks act as execution entry points; salary business logic and dashboard generation live in their respective modules. Aggregations belong in marts and source-specific parsing belongs in adapters. Test fixtures support validation and have no production ingestion path.
