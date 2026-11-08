# Vietnam IT Job Market Lakehouse

A daily pipeline for IT job data in Vietnam. It collects public ITviec posts and shows role demand and skill tags on a Databricks dashboard.

The main questions are:

- Which role families appear most often, and how do their counts change across collected days?
- Which skills are mentioned for a selected role, and how does their share change over time?

Choose a role in the dashboard to compare its skills and collected snapshots. Skills come from public tags, not the full list of mandatory requirements. [How role analysis works](docs/role_analysis.md).

## How it works

```mermaid
flowchart LR
    A[Collect jobs and FX rates] --> B[Save raw files]
    B --> C[Load Bronze with PySpark]
    C --> D[Build Silver and Gold with dbt]
    D --> E[Refresh dashboard]
```

GitHub Actions starts the Databricks Job at **08:00 Vietnam time** each day and waits for the result. GitHub may delay scheduled runs.

| Tool | Used for |
|---|---|
| Python | Read job pages and parse salary text |
| Parquet + Unity Catalog Volume | Store raw batches |
| PySpark + Delta Lake | Load Bronze and keep observation history |
| dbt | Clean data, build reports, and run data tests |
| Terraform | Create workspace resources |
| GitHub Actions | Run CI and schedule the pipeline |

## Run it

You need Python 3.12 or 3.13, uv, Terraform >=1.9, and a Databricks workspace with Unity Catalog and a serverless SQL warehouse. The workspace must be able to reach ITviec and the FX provider.

```powershell
uv sync --locked --extra dev
Copy-Item .env.example .env
```

Fill in `.env`, then run:

```powershell
uv run it-jobs check
uv run python scripts/deploy.py
uv run python scripts/deploy.py --apply
uv run it-jobs run --job-id YOUR_JOB_ID
```

Use the Job ID from the Terraform output. Keep `.env`, Terraform state, and raw data out of Git.

See the [runbook](docs/runbook.md) for GitHub setup, WSL login, replay, and repair.

## Results and limits

The check on **7 November 2026** collected 632 posts from 315 companies. Local tests and the cloud pipeline passed. dbt reported one expected warning because no public salaries could be used for an average. [Test results and links](docs/verification.md).

The project uses one source in Vietnam. Role names are assigned by title rules, with unmatched posts kept as `Other`. The history is still short and does not show the whole market. Hidden salaries stay `NULL`. Databricks Free Edition has usage limits.

## Tests

```powershell
uv run ruff check .
uv run pytest -q
```

CI also checks dbt parsing and Terraform configuration. Missing salary data produces a warning, not made-up values.

## More details

- [Project overview](docs/project_overview.md)
- [Architecture](docs/architecture.md)
- [Tables and fields](docs/data_dictionary.md)
- [Source rules](docs/source_contract.md)
- [Repository structure](docs/project_structure.md)
- [Learning guide](docs/portfolio_learning_guide.md)

Sources: [ITviec](https://itviec.com/it-jobs) and [Rates By Exchange Rate API](https://www.exchangerate-api.com). Raw FX responses stay private; see the [FX endpoint terms](https://www.exchangerate-api.com/docs/free).
