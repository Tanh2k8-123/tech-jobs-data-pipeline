with expected as (
    select source, snapshot_date, count(*) as posting_count
    from {{ ref('fct_job_daily_snapshots') }} group by source, snapshot_date
), actual as (
    select source, snapshot_date, sum(posting_count) as posting_count
    from {{ ref('mart_daily_role_demand') }} group by source, snapshot_date
)
select e.source, e.snapshot_date from expected e
left join actual a on e.source = a.source and e.snapshot_date = a.snapshot_date
where a.posting_count is null or e.posting_count <> a.posting_count
