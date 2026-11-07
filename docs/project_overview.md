# Project overview: Vietnam IT Job Market Lakehouse

## Objective and scope

Build a real daily batch pipeline for analyzing hiring skills and posting dates in Vietnam. The implemented source is verified public ITviec content. The pipeline does not depend on an assumed TopDev API or a synthetic-data fallback.

## Stack

Python with requests/BeautifulSoup collects source data; PyArrow writes Parquet; the Databricks SDK submits/waits for Jobs and supports replay uploads; a Unity Catalog Volume preserves raw batches; PySpark and Delta maintain Bronze; dbt-databricks builds Silver/Gold and tests; AI/BI Dashboard presents results; Terraform manages workspace resources; GitHub Actions owns scheduling.

Databricks Free Edition is a learning environment with quotas and no SLA, not a promise of unlimited free operation. Workspace egress to ITviec and FX has been verified. Ingestion runs inside Databricks because the GitHub runner encountered source-access errors. GitHub usage depends on the repository type, runner, and applicable allowances.

## Design improvements

1. A verified source implementation and explicit contract cover pagination, source IDs, JSON-LD publication dates, salary visibility, and completeness checks.
2. Immutable raw batches use checksums/manifests. Bronze preserves observations instead of overwriting all history with a job-ID-only MERGE.
3. `posted_date`, `first_seen_at`, and `snapshot_date` have separate meanings. A missing observation does not automatically mark a posting closed.
4. Skill dimensions and job–skill bridges have distinct roles. A city bridge handles multi-city postings at the correct grain.
5. Salary parsing is tested. Missing bounds, annual pay periods, and FX rates are not invented.
6. Advertised salary estimates include sample counts and coverage. Hidden salaries remain NULL and do not represent the entire market.
7. One scheduler triggers the Job, waits for its result, supports controlled retries/replay/repair, and refreshes the dashboard after a successful dbt build.
8. The repository includes package boundaries, dependency/provider locks, CI, a data dictionary, a runbook, and a learning guide.

## Difficulty

Approximately 7/10 for someone with basic Python/SQL. Handling a changing source, validating analytical semantics, and integrating cloud permissions/runtime behavior are the hardest parts. The MVP does not require streaming or multiple services. Spark supports lakehouse practice; this data volume is not presented as a big-data workload.

## Rubric evidence

The reviewed official rubric has seven criteria worth up to four points each: 28 technical points. Earlier references to 22/22 and a table totaling 26 were incorrect. The objective is to provide evidence for each criterion rather than award full marks for listing tools.

| Criterion | Required evidence |
|---|---|
| Problem | Clear questions, source limitations, and metric definitions |
| Cloud + IaC | Terraform plan/apply, deployed workspace resources, and privately retained state |
| Orchestration | A real ingestion-to-dashboard execution with failures propagated to the caller |
| Warehouse | Delta models with explicit grain, a clustering rationale, and query profiles |
| Transformation | dbt models, parser behavior, and cloud test results |
| Dashboard | Skill, posting-date, salary, and coverage charts; screenshots or access-appropriate links |
| Reproducibility | A clean checkout, locked dependencies, configuration examples, deployment instructions, and replay |

See the [README](../README.md) for deployment and [architecture.md](architecture.md) for operating limits, including the lack of a single atomic dbt transaction across all Gold tables.
