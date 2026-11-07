{{ config(severity='warn') }}
select 'low_salary_coverage' as warning
from {{ ref('fct_job_postings') }}
where observed_in_latest_snapshot
having count(avg_salary_usd) * 1.0 / nullif(count(*), 0) < 0.1
