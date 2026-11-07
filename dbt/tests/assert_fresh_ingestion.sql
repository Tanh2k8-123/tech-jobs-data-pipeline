select 'stale_ingestion' as failure
where (select max(completed_at) from {{ ref('stg_ingestion_runs') }})
    < current_timestamp() - interval 48 hours
