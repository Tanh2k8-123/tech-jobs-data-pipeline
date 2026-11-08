with role_counts as (
    select snapshot_date, sum(posting_count) as role_posting_count
    from ${catalog}.${prefix}_gold.mart_daily_role_demand
    where :role_family = 'All roles' or role_family = :role_family
    group by snapshot_date
), skill_counts as (
    select snapshot_date, skill_name, sum(posting_count) as posting_count
    from ${catalog}.${prefix}_gold.mart_daily_role_skills
    where :role_family = 'All roles' or role_family = :role_family
    group by snapshot_date, skill_name
), top_skills as (
    select skill_name, posting_count from skill_counts
    where snapshot_date = (select max(snapshot_date) from role_counts)
    order by posting_count desc, skill_name limit 5
)
select r.snapshot_date, t.skill_name,
    coalesce(s.posting_count, 0) as posting_count, r.role_posting_count,
    case when r.role_posting_count > 0 then
        round(100.0 * coalesce(s.posting_count, 0) / r.role_posting_count, 1)
    end as skill_share_pct
from role_counts r cross join top_skills t
left join skill_counts s on r.snapshot_date = s.snapshot_date and t.skill_name = s.skill_name
order by r.snapshot_date, t.skill_name
