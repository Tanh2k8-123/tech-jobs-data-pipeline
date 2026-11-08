with totals as (
    select role_family, sum(posting_count) as role_posting_count
    from ${catalog}.${prefix}_gold.mart_daily_role_demand
    where snapshot_date = (select max(snapshot_date)
        from ${catalog}.${prefix}_gold.mart_daily_role_demand)
        and (:role_family = 'All roles' or role_family = :role_family)
    group by role_family
), counts as (
    select role_family, skill_name, sum(posting_count) as posting_count
    from ${catalog}.${prefix}_gold.mart_daily_role_skills
    where snapshot_date = (select max(snapshot_date)
        from ${catalog}.${prefix}_gold.mart_daily_role_demand)
        and (:role_family = 'All roles' or role_family = :role_family)
    group by role_family, skill_name
), ranked as (
    select c.*, t.role_posting_count,
        round(100.0 * c.posting_count / t.role_posting_count, 1) as skill_share_pct,
        row_number() over (partition by c.role_family
            order by c.posting_count desc, c.skill_name) as skill_rank
    from counts c inner join totals t on c.role_family = t.role_family
)
select role_family, skill_name, posting_count, role_posting_count, skill_share_pct
from ranked
where skill_rank <= case when :role_family = 'All roles' then 3 else 15 end
order by role_family, skill_rank
