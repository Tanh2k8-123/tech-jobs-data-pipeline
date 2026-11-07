select job_sk, skill_sk as dimension_value from {{ ref('bridge_job_skills') }}
group by job_sk, skill_sk having count(*) > 1
union all
select job_sk, city_name as dimension_value from {{ ref('bridge_job_cities') }}
group by job_sk, city_name having count(*) > 1
