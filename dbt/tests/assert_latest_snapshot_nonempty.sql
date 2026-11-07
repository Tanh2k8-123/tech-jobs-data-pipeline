select 'empty_latest_snapshot' as failure
where (select count(*) from {{ ref('fct_job_postings') }} where observed_in_latest_snapshot) = 0
