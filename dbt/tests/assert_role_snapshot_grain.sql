select snapshot_sk, skill_sk as dimension_value
from {{ ref('bridge_job_snapshot_skills') }}
group by snapshot_sk, skill_sk having count(*) > 1
union all
select source, cast(snapshot_date as string) as dimension_value
from {{ ref('mart_daily_role_demand') }}
group by source, snapshot_date, role_sk having count(*) > 1
