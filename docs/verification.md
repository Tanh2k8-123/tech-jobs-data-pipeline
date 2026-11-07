# Verification evidence

Verification date: 7 November 2026, Vietnam time.

## Real source data

- ITviec extraction covered 32 listing pages, 632 postings, and 632 JobPosting detail pages.
- Batch: `20261107T131542_59cafb1db68e`.
- Direct Gold queries on Databricks returned 632 known postings, 632 postings in the latest snapshot, and zero missing publication dates.
- Zero salary samples qualified for a midpoint because the source hid salaries. No replacement samples were generated.
- FX data came from the live endpoint, retained its provider timestamp, and was preserved privately with the raw batch.

## Local and cloud checks

- 27 Python/SQL business-semantic tests passed.
- Ruff, dbt parse, and Terraform fmt/validate passed.
- Job `198306811950277`, run `559940590723474`: Bronze, dbt build, and dashboard refresh all succeeded.
- Cloud dbt execution completed two seeds, eight table models, five view models, and 38 data tests. There were 37 passing tests, one salary-coverage warning, and zero errors. Across all 53 operations: PASS=52, WARN=1.
- Replaying the same batch through Bronze, run `218432312513077`, retained 632 observations and one batch, verifying idempotency on real Delta tables.

## Complete cloud automation

- Ubuntu CI passed: [Validate pipeline](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380766623).
- Source ingestion runs on Databricks and does not depend on a personal machine or source access from the GitHub runner.
- Databricks run `791920414056791` collected real raw data, then successfully repaired Bronze → dbt → dashboard after a parameter-name collision was fixed. Bronze uses a separate `raw_path` input so the Job's `input_path` cannot override the task value.
- The [successful GitHub workflow](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380817065) verified failed-run repair and waiting for Job SUCCESS.
- After two real batches: Bronze held 1,264 observations across two batches; Gold held 632 postings, 315 companies, and 320 skill tags. The latest snapshot had 632 postings, no missing publication dates, and no publicly available salary midpoints.
- `01:00 UTC` equals `08:00` in Vietnam. Scheduling was enabled with `ENABLE_DAILY_PIPELINE=true`. Scheduled runs have no `repair_run_id` and collect a fresh snapshot.

The following links require workspace access:

- [Databricks Job](https://dbc-63d22f94-de5b.cloud.databricks.com/#job/198306811950277)
- [AI/BI Dashboard](https://dbc-63d22f94-de5b.cloud.databricks.com/dashboardsv3/01f1daaffcd713898cd8c43b363dce39/published)

Deployment repository: [Tanh2k8-123/tech-jobs-data-pipeline](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline).

The GitHub Actions PAT was created with an expiry of 5 February 2027 and must be rotated before then. Its value is stored in GitHub Secrets, not in source code or documentation.
