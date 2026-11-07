select distinct skill_sk, skill_name from {{ ref('int_job_skills') }}
