with counts as (
    select f.source, f.snapshot_date, f.role_sk, f.role_family,
        d.skill_sk, d.skill_name, count(distinct f.job_sk) as posting_count
    from {{ ref('fct_job_daily_snapshots') }} f
    inner join {{ ref('bridge_job_snapshot_skills') }} b on f.snapshot_sk = b.snapshot_sk
    inner join {{ ref('dim_skills') }} d on b.skill_sk = d.skill_sk
    left join {{ ref('role_tag_labels') }} role_tag on lower(d.skill_name) = role_tag.skill_name
    where role_tag.skill_name is null
    group by f.source, f.snapshot_date, f.role_sk, f.role_family, d.skill_sk, d.skill_name
)
select c.*, r.posting_count as role_posting_count,
    c.posting_count * 1.0 / r.posting_count as skill_share
from counts c
inner join {{ ref('mart_daily_role_demand') }} r
    on c.source = r.source and c.snapshot_date = r.snapshot_date and c.role_sk = r.role_sk
where r.posting_count > 0
