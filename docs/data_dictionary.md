# Data dictionary

| Relation | Grain and purpose |
|---|---|
| Bronze `raw_it_job_observations` | One observation per source + source_job_id + run_id; preserves source payload and parser results |
| Bronze `ingestion_runs` | One run with a completed Bronze load |
| Silver `stg_job_history` | Valid observation history joined to the completion ledger; casts types, converts FX, and parses arrays |
| Silver `int_jobs_current` | Latest observation per source posting, with first_seen_at/last_seen_at |
| Gold `fct_job_postings` | One observed source posting, with its latest-snapshot presence flag |
| Gold `dim_companies` | One company identity within a source; no automatic cross-source entity resolution |
| Gold `dim_skills` | One normalized skill name |
| Gold `bridge_job_skills` | One unique posting–skill pair |
| Gold `bridge_job_cities` | One unique posting–city pair |
| Gold `mart_skill_demand` | One skill, measured over each source's latest complete snapshot |
| Gold `mart_daily_city_jobs` | One posting-date–city combination, measured over all observed postings |
| Gold `audit_data_quality` | One source, with missing-data and freshness metrics |

## Important fields

- `job_sk`: SHA-256 of the source and posting ID, using length prefixes to avoid ambiguous concatenations.
- `posted_date`: the publication date supplied by the source. Missing dates are excluded from the posting-date chart and counted in the audit table.
- `snapshot_date`: the Vietnam calendar date of collection. `ingested_at`, `first_seen_at`, `last_seen_at`, and `fx_rate_at` represent UTC timestamps.
- `observed_in_latest_snapshot`: present in the source's latest complete run. It is not named `is_open` because presence/absence alone does not establish opening or closing status.
- `min_salary_usd`, `max_salary_usd`: known monthly bounds in USD; either may be NULL.
- `avg_salary_usd`: midpoint when both bounds are known; NULL for one-sided or undisclosed salaries.
- `salary_sample_count`: postings with a valid salary midpoint in the skill group.
- `salary_coverage`: midpoint sample count / posting count in the skill group. It is not an estimate of salary disclosure across the entire market.
- `salary_basis`: `unknown` unless the source establishes gross/net treatment.
- `city_name`: Ha Noi / Ho Chi Minh / Da Nang / Other. A posting may have multiple values through the bridge.

Skills absent from the alias seed retain a lowercase name rather than being assigned an inferred taxonomy. Add mappings only with supporting evidence and keep aliases unique. Vietnamese source aliases in seeds are intentional input data; normalized outputs and repository documentation use English.
