with exploded as (
    select job_sk, lower(trim(skill)) as skill_alias
    from {{ ref('int_jobs_current') }}
    lateral view explode(skills) exploded as skill
), normalized as (
    select e.job_sk, coalesce(a.skill_name, e.skill_alias) as skill_name
    from exploded e
    left join {{ ref('skill_aliases') }} a on e.skill_alias = a.skill_alias
    where e.skill_alias <> ''
)
select distinct job_sk, skill_name,
    {{ stable_key(['skill_name']) }} as skill_sk
from normalized
