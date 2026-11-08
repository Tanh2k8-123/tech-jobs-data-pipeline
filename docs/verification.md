# Test results

These results are from **7 November 2026**. Counts will change as new batches arrive.

| Check | Result |
|---|---|
| Source collection | 32 listing pages and 632 detail pages |
| Gold data | 632 posts, 315 companies, 320 skill tags |
| Missing publication dates | 0 |
| Salary midpoint samples | 0; salaries were hidden |
| Local tests | 27 passed |
| dbt data tests | 37 passed, 1 salary-coverage warning, 0 errors |
| Code/config checks | Ruff, dbt parse, Terraform fmt/validate passed |

After two batches, Bronze held 1,264 observations while Gold held 632 posts. Loading the same first batch again kept 632 observations and one batch, which checked idempotency on Delta.

## Run evidence

- [CI passed](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380766623).
- [GitHub repair workflow passed](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380817065).
- Databricks run `559940590723474` completed Bronze, dbt, and dashboard refresh.
- Run `218432312513077` checked loading the same batch again.
- Run `791920414056791` collected data on Databricks. After fixing a parameter-name collision, repair completed the remaining tasks. Bronze now uses `raw_path`, separate from the Job's `input_path`.

The daily schedule was enabled at 08:00 Vietnam time. Scheduled runs collect new data.

These links need workspace access:

- [Databricks Job](https://dbc-63d22f94-de5b.cloud.databricks.com/#job/198306811950277)
- [Dashboard](https://dbc-63d22f94-de5b.cloud.databricks.com/dashboardsv3/01f1daaffcd713898cd8c43b363dce39/published)

## Role analysis added on 8 November 2026

- 52 local tests passed, including title rules, same-day batch selection, historical skills, and role-filtered queries.
- Databricks run `687396012895547` rebuilt dbt models and refreshed the dashboard using existing Bronze data. All 66 data tests completed: 65 passed and one expected salary warning.
- Daily facts selected 632 posts for 7 November and 629 for 8 November, using the last complete batch on each day.
- Queries were checked with All roles, Data Engineer, and Backend Developer. The selected role changes the denominator as well as the skill counts.
- Under the current title rules, the latest snapshot has 16 Data Engineer posts. Python and SQL each appear in 10 posts (62.5%). These are source-tag mentions, not full mandatory requirements.

The dashboard exposes title-label issues and collected-day counts. Two days of data are not enough to infer a long-term market trend. See [role analysis](role_analysis.md).
