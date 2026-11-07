with ranked as (
    select company_sk, source, company_id, company_name,
        row_number() over (partition by company_sk order by last_seen_at desc, job_sk) as name_rank
    from {{ ref('int_jobs_current') }}
)
select company_sk, source, company_id, company_name from ranked where name_rank = 1
