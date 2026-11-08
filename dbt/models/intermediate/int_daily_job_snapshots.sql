with ranked_runs as (
    select *, row_number() over (
        partition by source, snapshot_date order by completed_at desc, run_id desc
    ) as day_run_rank
    from {{ ref('stg_ingestion_runs') }}
)
select h.*, r.completed_at as collected_at,
    {{ stable_key(['h.job_sk', 'h.snapshot_date']) }} as snapshot_sk
from {{ ref('int_job_role_history') }} h
inner join ranked_runs r on h.run_id = r.run_id and r.day_run_rank = 1
