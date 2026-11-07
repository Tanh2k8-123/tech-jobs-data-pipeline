with ranked as (
    select *,
        min(first_observed_at) over (partition by job_sk) as first_seen_at,
        max(ingested_at) over (partition by job_sk) as last_seen_at,
        row_number() over (
            partition by job_sk order by ingested_at desc, run_id desc
        ) as observation_rank
    from {{ ref('stg_job_history') }}
), latest_runs as (
    select source, run_id,
        row_number() over (partition by source order by completed_at desc, run_id desc) as run_rank
    from {{ ref('stg_ingestion_runs') }}
)
select r.* except (observation_rank),
    (r.min_salary_usd + r.max_salary_usd) / 2.0 as avg_salary_usd,
    r.run_id = latest.run_id as observed_in_latest_snapshot
from ranked r
inner join latest_runs latest on r.source = latest.source and latest.run_rank = 1
where r.observation_rank = 1
