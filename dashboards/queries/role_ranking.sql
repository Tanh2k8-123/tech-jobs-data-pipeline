select role_family, sum(posting_count) as posting_count
from ${catalog}.${prefix}_gold.mart_daily_role_demand
where snapshot_date = (
    select max(snapshot_date) from ${catalog}.${prefix}_gold.mart_daily_role_demand
)
group by role_family
having sum(posting_count) > 0
order by posting_count desc, role_family
limit 15
