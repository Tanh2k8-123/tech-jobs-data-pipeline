with ranked as (
    select company_sk, source, company_id, company_name,
        row_number() over (partition by company_sk order by ingested_at desc, job_sk) as name_rank
    from {{ ref('int_job_role_history') }}
)
select company_sk, source, company_id, company_name from ranked where name_rank = 1
