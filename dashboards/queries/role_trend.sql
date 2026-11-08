with top_roles as (
    select role_family, sum(posting_count) as latest_count
    from ${catalog}.${prefix}_gold.mart_daily_role_demand
    where snapshot_date = (
        select max(snapshot_date) from ${catalog}.${prefix}_gold.mart_daily_role_demand
    ) and role_family <> 'Other'
    group by role_family
    having sum(posting_count) > 0
    order by latest_count desc, role_family limit 6
)
select snapshot_date, role_family, sum(posting_count) as posting_count
from ${catalog}.${prefix}_gold.mart_daily_role_demand
where (:role_family = 'All roles' and role_family in (select role_family from top_roles))
    or role_family = :role_family
group by snapshot_date, role_family
order by snapshot_date, role_family
