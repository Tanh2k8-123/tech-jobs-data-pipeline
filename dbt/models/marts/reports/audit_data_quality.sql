select
    source, count(*) as known_jobs,
    sum(case when observed_in_latest_snapshot then 1 else 0 end) as latest_snapshot_jobs,
    sum(case when avg_salary_usd is not null then 1 else 0 end) as salary_sample_count,
    sum(case when salary_parse_status = 'unsupported' then 1 else 0 end) as salary_parse_failures,
    sum(case when posted_date is null then 1 else 0 end) as missing_posted_date,
    max(last_seen_at) as data_updated_at
from {{ ref('fct_job_postings') }} group by source
