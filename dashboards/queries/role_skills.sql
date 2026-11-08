with total as (
    select sum(posting_count) as role_posting_count
    from ${catalog}.${prefix}_gold.mart_daily_role_demand
    where snapshot_date = (select max(snapshot_date)
        from ${catalog}.${prefix}_gold.mart_daily_role_demand)
        and (:role_family = 'All roles' or role_family = :role_family)
)
select s.skill_name, sum(s.posting_count) as posting_count,
    max(t.role_posting_count) as role_posting_count,
    round(100.0 * sum(s.posting_count) / max(t.role_posting_count), 1) as skill_share_pct
from ${catalog}.${prefix}_gold.mart_daily_role_skills s cross join total t
where s.snapshot_date = (select max(snapshot_date)
    from ${catalog}.${prefix}_gold.mart_daily_role_demand)
    and (:role_family = 'All roles' or s.role_family = :role_family)
group by s.skill_name
order by posting_count desc, s.skill_name
limit 15
