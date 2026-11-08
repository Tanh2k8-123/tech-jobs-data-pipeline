{{ config(materialized='table') }}
with normalized as (
    select *, {{ normalized_job_title('title') }} as normalized_title
    from {{ ref('stg_job_history') }}
), cleaned as (
    select *, regexp_replace(
        normalized_title, r'^[ ]*(?:(?:\[[^]]*\]|\([^)]*\))[ ]*)+', ''
    ) as title_without_level_prefix
    from normalized
), titles as (
    select *, trim(split_part(split_part(title_without_level_prefix, '(', 1), '[', 1))
        as primary_title
    from cleaned
), candidates as (
    select h.*, r.rule_id, r.priority, r.role_family,
        case when regexp_like(h.primary_title, r.title_pattern) then 0
             when r.rule_id is not null then 1 else 2 end as match_tier,
        sum(case when regexp_like(h.primary_title, r.title_pattern)
            and r.rule_id <> 'software' then 1 else 0 end)
            over (partition by h.job_sk, h.run_id) as primary_role_matches
    from titles h
    left join {{ ref('role_rules') }} r
        on regexp_like(h.primary_title, r.title_pattern)
        or regexp_like(h.normalized_title, r.title_pattern)
), ranked as (
    select *, row_number() over (
        partition by job_sk, run_id order by match_tier, priority, rule_id
    ) as role_rank
    from candidates
), chosen as (
    select * except (role_family, priority, match_tier, role_rank),
        coalesce(role_family, 'Other') as role_family,
        case when rule_id is null then 'unclassified'
             when match_tier = 1 then 'full_title_match'
             when primary_role_matches > 1 then 'multiple_primary_matches'
             when rule_id = 'software' then 'generic_title_match'
             else 'primary_title_match' end as role_classification
    from ranked where role_rank = 1
)
select *, {{ stable_key(['role_family']) }} as role_sk from chosen
