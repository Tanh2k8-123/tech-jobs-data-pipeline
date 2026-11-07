select r.run_id
from {{ ref('stg_ingestion_runs') }} r
left join {{ ref('stg_job_history') }} h on r.run_id = h.run_id
group by r.run_id, r.row_count
having count(h.job_sk) <> r.row_count or r.row_count < 1
