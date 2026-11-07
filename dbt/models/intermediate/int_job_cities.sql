with exploded as (
    select job_sk, lower(trim(location)) as city_alias
    from {{ ref('int_jobs_current') }}
    lateral view explode(locations) exploded as location
)
select distinct e.job_sk, coalesce(a.city_name, 'Other') as city_name
from exploded e
left join {{ ref('city_aliases') }} a on e.city_alias = a.city_alias
