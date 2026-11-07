# Operations runbook

## Connection checks

Run `uv run it-jobs check` from the repository root. The CLI loads `.env`, checks the current user, warehouse, and catalog, and executes SELECT 1 without printing credentials. For WSL OAuth, keep the selected profile signed in and the Databricks CLI available at `/usr/local/bin/databricks`. Select an HTTP path explicitly when multiple warehouses exist. With a single warehouse, the CLI can discover it and append its non-secret HTTP path to an existing `.env` file.

## Deployment

Run `uv run python scripts/deploy.py` to inspect a plan, then `uv run python scripts/deploy.py --apply`. Preserve `infra/terraform/terraform.tfstate`; keep state and plans out of Git. Terraform receives an ephemeral OAuth bearer token through its process environment, not a token file. The dashboard is created inside the workspace, is not shared publicly, and does not embed credentials.

Read `job_id` from Terraform outputs. `uv run it-jobs run --job-id ID` starts the complete real-source DAG on Databricks and waits for completion. An empty Job `input_path` requests a new extraction; Bronze receives a concrete `raw_path` through a task value. Replay supplies an existing path and skips fresh extraction.

## Recovery and backfills

- **Extraction fails before its manifest:** the batch is incomplete and must not enter Bronze. Inspect source availability, robots.txt, pagination, JSON-LD, and logs before rerunning extraction.
- **Upload is interrupted:** replay the exact saved raw directory. Existing files must match their checksums and are never overwritten with different content.
- **Spark fails:** retry the same batch. Observation and ledger MERGEs are idempotent.
- **dbt fails:** inspect the failed model/test in the Job, deploy the fix, and replay the batch. Dashboard refresh must not proceed after a failed build.
- **Extraction already succeeded:** use `it-jobs repair --job-id ID --run-id RUN_ID` or the workflow's `repair_run_id` input to rerun failed tasks and their dependents. Give task-value-derived inputs distinct names so automatic Job-parameter propagation cannot overwrite them.
- **The source hides salaries:** NULL results and a coverage warning are expected. Do not replace missing values with zero or invent samples to suppress the warning.
- **Historical backfill:** replay preserved raw runs. Rebuilding a workspace entirely from old batches triggers the freshness check by design; collect a current snapshot before publishing a current dashboard.

## Monitoring

Monitor posting/page counts, last update time, salary coverage, parse failures, and missing publication dates. The latest snapshot does not establish opening or closing status. The time series does not reconstruct all hiring activity before the pipeline began observing the source.

The GitHub workflow has a 150-minute timeout, concurrency control, and seven-day failure-log retention. Do not publish raw Parquet/FX responses as workflow artifacts. Check Databricks quotas before increasing frequency. Monitor raw storage; no automatic deletion task is configured.
