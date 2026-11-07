select job_sk, city_name from {{ ref('int_job_cities') }}
