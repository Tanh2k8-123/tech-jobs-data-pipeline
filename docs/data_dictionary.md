# Tables and fields

## Tables

| Table | One row means |
|---|---|
| `raw_it_job_observations` | One source post observed in one batch |
| `ingestion_runs` | One completed Bronze load |
| `stg_job_history` | One valid observation with typed fields and converted salary bounds |
| `int_jobs_current` | The latest observation of one post |
| `fct_job_postings` | One post with its current values |
| `dim_companies` | One company ID within a source |
| `dim_skills` | One normalized skill |
| `bridge_job_skills` | One post–skill pair |
| `bridge_job_cities` | One post–city pair |
| `mart_skill_demand` | One skill with posting and salary counts |
| `mart_daily_city_jobs` | One publication date and city |
| `audit_data_quality` | One source with quality counts |
| `int_job_role_history` | One observation with its title-based role label |
| `dim_job_roles` | One role family, including Other |
| `fct_job_daily_snapshots` | One post in the last complete batch for a source/day |
| `bridge_job_snapshot_skills` | One daily snapshot–skill pair |
| `mart_daily_role_demand` | One collected source/day and role family |
| `mart_daily_role_skills` | One collected source/day, role, and skill |

## Fields to know

- `job_sk`: a stable hash of the source and post ID.
- `posted_date`: the date given by the website.
- `snapshot_date`: the Vietnam date when the batch was collected.
- `first_seen_at` / `last_seen_at`: the first/latest observation times, in UTC.
- `observed_in_latest_snapshot`: present in the source's latest complete batch. It does not prove the job is still open.
- `min_salary_usd` / `max_salary_usd`: known monthly salary bounds.
- `avg_salary_usd`: midpoint when both bounds are known.
- `salary_sample_count`: posts with a valid midpoint.
- `salary_coverage`: salary sample count divided by posting count.
- `salary_basis`: `unknown` unless gross/net is stated.
- `city_name`: Ha Noi, Ho Chi Minh, Da Nang, or Other.
- `role_family`: one primary role label assigned by title rules.
- `role_classification`: how the title matched, including generic, multiple-match, and unclassified cases.
- `snapshot_sk`: a stable key for one post on one selected snapshot day.
- `skill_share`: posts mentioning a skill / all posts in that role and snapshot. Dashboard queries convert this fraction to a percentage.

Unmapped skills stay lowercase. Vietnamese aliases in seeds are source inputs. Company IDs from different sources are not automatically merged.

Role labels and daily skill shares are explained in [role_analysis.md](role_analysis.md). The current fact keeps latest attributes; daily facts keep the attributes observed in each selected daily batch.
