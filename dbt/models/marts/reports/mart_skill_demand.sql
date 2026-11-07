select
    d.skill_sk, d.skill_name,
    count(distinct f.job_sk) as job_count,
    count(f.avg_salary_usd) as salary_sample_count,
    avg(f.avg_salary_usd) as avg_salary_usd,
    count(f.avg_salary_usd) * 1.0 / count(distinct f.job_sk) as salary_coverage,
    max(f.last_seen_at) as data_updated_at
from {{ ref('fct_job_postings') }} f
inner join {{ ref('bridge_job_skills') }} b on f.job_sk = b.job_sk
inner join {{ ref('dim_skills') }} d on b.skill_sk = d.skill_sk
where f.observed_in_latest_snapshot
group by d.skill_sk, d.skill_name
