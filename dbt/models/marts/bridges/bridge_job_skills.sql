select job_sk, skill_sk from {{ ref('int_job_skills') }}
