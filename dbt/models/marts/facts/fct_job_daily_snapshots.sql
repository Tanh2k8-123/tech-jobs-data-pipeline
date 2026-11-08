{{ config(liquid_clustered_by=['snapshot_date', 'role_family']
          if var('enable_liquid_clustering') else none) }}
select snapshot_sk, job_sk, company_sk, source, source_job_id, title, job_url,
    snapshot_date, posted_date, collected_at, run_id,
    role_sk, role_family, rule_id as role_rule_id, role_classification,
    primary_role_matches
from {{ ref('int_daily_job_snapshots') }}
