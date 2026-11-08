{{ config(liquid_clustered_by=['posted_date'] if var('enable_liquid_clustering') else none) }}
select
    job_sk, company_sk, source, source_job_id, job_url, title, posted_date,
    role_sk, role_family, rule_id as role_rule_id, role_classification,
    first_seen_at, last_seen_at, snapshot_date, run_id, observed_in_latest_snapshot,
    min_salary_usd, max_salary_usd, avg_salary_usd, salary_type,
    salary_parse_status, salary_basis, salary_currency, salary_period,
    fx_rate_at, fx_provider
from {{ ref('int_jobs_current') }}
