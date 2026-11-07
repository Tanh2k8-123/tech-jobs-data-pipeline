select
    {{ stable_key(['r.source', 'r.source_job_id']) }} as job_sk,
    {{ stable_key(['r.source', 'r.company_id']) }} as company_sk,
    r.source, r.source_job_id, r.company_id, r.company_name, r.title, r.job_url,
    r.salary_text, r.salary_basis, r.salary_type, r.salary_parse_status,
    r.salary_currency, r.salary_period, r.salary_min_native, r.salary_max_native,
    r.fx_vnd_per_usd, cast(r.fx_rate_at as timestamp) as fx_rate_at, r.fx_provider,
    case when r.salary_parse_status = 'parsed' and r.salary_period = 'month'
        then case r.salary_currency when 'USD' then r.salary_min_native
            when 'VND' then r.salary_min_native / r.fx_vnd_per_usd end
    end as min_salary_usd,
    case when r.salary_parse_status = 'parsed' and r.salary_period = 'month'
        then case r.salary_currency when 'USD' then r.salary_max_native
            when 'VND' then r.salary_max_native / r.fx_vnd_per_usd end
    end as max_salary_usd,
    from_json(r.skills_json, 'array<string>') as skills,
    from_json(r.locations_json, 'array<string>') as locations,
    cast(r.posted_date as date) as posted_date,
    cast(r.snapshot_date as date) as snapshot_date,
    cast(r.ingested_at as timestamp) as ingested_at,
    cast(r.first_observed_at as timestamp) as first_observed_at,
    r.run_id, r.payload_hash
from {{ source('bronze', 'raw_it_job_observations') }} r
inner join {{ ref('stg_ingestion_runs') }} runs on r.run_id = runs.run_id
