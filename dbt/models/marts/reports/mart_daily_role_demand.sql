with dates as (
    select distinct source, snapshot_date, collected_at
    from {{ ref('fct_job_daily_snapshots') }}
), counts as (
    select source, snapshot_date, role_sk,
        count(distinct job_sk) as posting_count,
        count(distinct company_sk) as company_count
    from {{ ref('fct_job_daily_snapshots') }}
    group by source, snapshot_date, role_sk
)
select d.source, d.snapshot_date, d.collected_at, r.role_sk, r.role_family,
    coalesce(c.posting_count, 0) as posting_count,
    coalesce(c.company_count, 0) as company_count
from dates d cross join {{ ref('dim_job_roles') }} r
left join counts c on d.source = c.source and d.snapshot_date = c.snapshot_date
    and r.role_sk = c.role_sk
