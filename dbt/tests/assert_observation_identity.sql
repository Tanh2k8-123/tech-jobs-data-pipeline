select job_sk, run_id from {{ ref('stg_job_history') }}
group by job_sk, run_id having count(*) > 1
