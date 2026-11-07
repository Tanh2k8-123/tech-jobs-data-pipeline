select job_sk from {{ ref('fct_job_postings') }}
where min_salary_usd < 0 or max_salary_usd < 0
    or min_salary_usd > max_salary_usd
    or (salary_type = 'upper_bound' and min_salary_usd is not null)
    or (salary_type = 'lower_bound' and max_salary_usd is not null)
    or (salary_parse_status <> 'parsed' and avg_salary_usd is not null)
    or (avg_salary_usd is not null and
        abs(avg_salary_usd - (min_salary_usd + max_salary_usd) / 2.0) > 0.00001)
