select snapshot_sk, job_sk, skill_sk from {{ ref('int_daily_job_skills') }}
