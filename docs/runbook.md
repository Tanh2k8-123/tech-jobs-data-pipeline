# Run the project

## 1. Set up

For a new checkout:

```powershell
uv sync --locked --extra dev
Copy-Item .env.example .env
```

Fill in the host, token, and SQL HTTP path in `.env`. Use `workspace` as the catalog and `vn_jobs` as the schema prefix unless you choose others.

For OAuth in WSL, use `DATABRICKS_WSL_PROFILE=your-profile` with the host and HTTP path. On Windows, this uses the CLI at `/usr/local/bin/databricks` inside WSL.

## 2. Deploy and run

```powershell
uv run it-jobs check
uv run python scripts/deploy.py
uv run python scripts/deploy.py --apply
uv run it-jobs run --job-id YOUR_JOB_ID
```

`check` tests the connection. The first deployment command shows a plan; `--apply` creates or updates resources. Take the Job ID from its output.

Keep the Terraform state file. Do not commit state, plans, tokens, or raw data.

## 3. Set up GitHub

Add repository Secrets: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_HTTP_PATH`.

Add Variables: `PIPELINE_JOB_ID`, `DATABRICKS_CATALOG`, `SCHEMA_PREFIX`. Run **Daily Vietnam IT jobs** manually, then set `ENABLE_DAILY_PIPELINE=true`.

The schedule is `01:00 UTC` / `08:00` Vietnam time. GitHub may start it late.

Optional setup helper:

```powershell
uv run python scripts/configure_github.py --repo OWNER/REPO --job-id YOUR_JOB_ID
```

This keeps an existing token secret or creates a 90-day PAT. It sends the token straight to GitHub Secrets and leaves the schedule disabled until you verify a run. The token created for this deployment expires on **5 February 2027**.

## 4. Recover a failed run

If extraction succeeded, repair the failed tasks and their dependents:

```powershell
uv run it-jobs repair --job-id YOUR_JOB_ID --run-id FAILED_RUN_ID
```

The manual GitHub workflow also accepts `repair_run_id`. Leave it empty for fresh collection.

To collect locally and replay a saved batch:

```powershell
uv run it-jobs extract
uv run it-jobs replay --input artifacts/landing/YYYY-MM-DD/RUN_ID --job-id YOUR_JOB_ID
```

Replay keeps the original batch date. Do not label today's data as a historical snapshot.

## If something goes wrong

| Problem | What to check |
|---|---|
| Source error | Website access, page structure, and extraction logs |
| Upload/Spark error | Saved batch path, checksum, and row count; retry the same batch |
| dbt error | Failed model/test; deploy the fix, then repair or replay |
| Missing salaries | NULL and a coverage warning are expected |
| Stale data | Check the latest successful run; collect a fresh snapshot |

Dashboard refresh stops after a failed build. Monitor posting counts, update times, missing dates, salary coverage, storage, and Databricks quotas. GitHub keeps failure logs for seven days. Raw data has no automatic cleanup.
