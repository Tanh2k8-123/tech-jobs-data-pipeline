# A simple guide to the project

Start here if you know basic Python and SQL. Follow one job post from the website to the dashboard.

## 1. Collect a job post

Read [itviec.py](../src/sea_it_jobs/sources/itviec.py).

- `parse_listing()` reads IDs, titles, skills, and detail links.
- `extract()` visits the listing pages.
- `parse_detail()` reads JobPosting JSON-LD from each detail page.

JSON-LD is JSON stored inside the HTML. It gives fields such as publication date and location. The output is a list of Python dictionaries.

[http.py](../src/sea_it_jobs/http.py) handles timeouts, retries, and the delay between requests. A page returning HTTP 200 can still have the wrong structure, so the parser checks its fields too.

## 2. Save a raw batch

Read `collect()` in [ingestion.py](../src/sea_it_jobs/ingestion.py).

Each batch contains:

```text
jobs.parquet    # Records and source payloads
fx.json         # The exchange-rate response used by this batch
manifest.json   # Batch ID, row count, checksum, and completion flag
```

The manifest is written last. It tells the next step that collection finished. The checksum detects changes to the Parquet file.

Raw files let you fix the processing code and use the same input again. `salary.py` parses salary text before it is saved. For example, `Up to $3000` has an upper bound and an unknown lower bound. Hidden salaries stay NULL.

## 3. Load Bronze

Read [01_load_bronze.py](../notebooks/01_load_bronze.py).

The notebook checks the manifest and loads observations into Delta. The key is:

```python
["source", "source_job_id", "run_id"]
```

The table's **grain** is what one row means: one observation of one source post in one batch.

| Action for a post | Observation rows |
|---|---:|
| Load batch R1 | 1 |
| Load R1 again | Still 1 |
| Collect and load a new R2 batch | 2 |

Loading the same input without adding duplicates is **idempotency**. A new batch adds history on purpose.

The notebook writes `ingestion_runs` last. Silver reads only batches in this ledger. A retry can finish the ledger without duplicating the observations.

The batch `run_id`, Databricks run ID, and GitHub run ID are different IDs. A replay can have a new Databricks execution but the same batch ID.

## 4. Clean data in Silver

Read these dbt models:

- [stg_job_history.sql](../dbt/models/staging/stg_job_history.sql): set types, read JSON arrays, and convert monthly salary bounds to USD.
- [int_jobs_current.sql](../dbt/models/intermediate/int_jobs_current.sql): keep the latest observation of each post.
- [int_job_skills.sql](../dbt/models/intermediate/int_job_skills.sql): split skill arrays and apply aliases from `dbt/seeds/`.

A dbt model is a SQL SELECT that becomes a view or table. `ref("model_name")` points to another model and tells dbt which model must run first. Most Silver models here are views.

The latest-record logic uses:

```sql
row_number() over (
    partition by job_sk
    order by ingested_at desc, run_id desc
)
```

This numbers observations within each post, newest first. Keeping row 1 gives the current record.

Keep the dates separate: `posted_date` comes from the website; `first_seen_at` and `last_seen_at` come from our observations. A post missing from the latest batch is not automatically marked closed.

## 5. Build Gold for reports

| Table type | Example | What it holds |
|---|---|---|
| Fact | `fct_job_postings` | One current record per post |
| Dimension | `dim_skills` | One normalized skill |
| Bridge | `bridge_job_skills` | One post–skill pair |
| Mart | `mart_skill_demand` | Skill counts and salary results |

A post with four skills has one fact row and four bridge rows. This keeps the many-to-many relationship clear. Always check what each row means before joining tables.

`COUNT(DISTINCT job_sk)` counts posts. `COUNT(avg_salary_usd)` counts only posts with a usable salary. High demand can come with no salary samples.

The SQL warehouse runs these queries; data stays in Delta tables.

## 6. Run the steps in order

The Databricks Job runs:

```text
extract_source → load_bronze → dbt_build → refresh_dashboard
```

GitHub Actions starts it each day and waits. `depends_on` sets task order. A failed dbt build stops dashboard refresh.

Use `run` for new data, `replay` for a saved local batch, and `repair` for failed tasks after extraction already succeeded. The [runbook](runbook.md) has the commands.

Terraform creates the workspace resources. `plan` shows proposed changes; `apply` makes them. Keep the state file so Terraform knows which resources it manages.

## 7. Check the result

Python tests cover the source parser, salary rules, and raw-file checks. dbt tests check keys, links between tables, row counts, and freshness.

Local SQL tests use DuckDB to check the calculations. They do not replace a Databricks run. CI checks code and config; the data workflow checks the real cloud pipeline.

## Try it yourself

Run these read-only queries on Databricks:

```sql
SELECT count(*) AS observations, count(DISTINCT run_id) AS batches
FROM workspace.vn_jobs_bronze.raw_it_job_observations;

SELECT count(*) AS posts
FROM workspace.vn_jobs_gold.fct_job_postings;

SELECT skill_name, job_count, salary_sample_count
FROM workspace.vn_jobs_gold.mart_skill_demand
ORDER BY job_count DESC, skill_name
LIMIT 15;
```

Explain why observations can outnumber posts, and why a skill can have posts but no salary samples.

A useful next exercise is adding one skill alias and testing its effect. A local CSV edit needs deployment and dbt seed/build before it changes cloud results.

For a portfolio discussion, explain the problem, follow one record through the pipeline, show test results, and name the limits. This project has one source, hidden salaries, a small dataset, and full Gold rebuilds. It does not prove big-data performance, and a failed build does not roll back all Gold tables together.
