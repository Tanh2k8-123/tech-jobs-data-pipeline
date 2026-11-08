select distinct skill_sk, skill_name from {{ ref('int_job_skills') }}
union
select distinct skill_sk, skill_name from {{ ref('int_daily_job_skills') }}
