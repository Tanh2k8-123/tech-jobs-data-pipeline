with ranked as (
    select *, row_number() over (
        partition by source, snapshot_date order by completed_at desc, run_id desc
    ) as day_rank
    from {{ ref('stg_ingestion_runs') }}
), actual as (
    select source, snapshot_date, count(*) as posting_count
    from {{ ref('fct_job_daily_snapshots') }} group by source, snapshot_date
)
select r.source, r.snapshot_date from ranked r
left join actual a on r.source = a.source and r.snapshot_date = a.snapshot_date
where r.day_rank = 1 and (a.posting_count is null or r.row_count <> a.posting_count)
