select
    source, run_id, input_path, parquet_sha256,
    cast(snapshot_date as date) as snapshot_date,
    cast(completed_at as timestamp) as completed_at,
    cast(row_count as bigint) as row_count
from {{ source('bronze', 'ingestion_runs') }}
