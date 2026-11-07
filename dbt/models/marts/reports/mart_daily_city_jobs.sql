select f.posted_date, b.city_name, count(distinct f.job_sk) as job_count
from {{ ref('fct_job_postings') }} f
inner join {{ ref('bridge_job_cities') }} b on f.job_sk = b.job_sk
where f.posted_date is not null and b.city_name in ('Ha Noi', 'Ho Chi Minh', 'Da Nang')
group by f.posted_date, b.city_name
