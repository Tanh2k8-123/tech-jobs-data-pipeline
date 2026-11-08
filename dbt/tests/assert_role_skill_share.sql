select role_family, skill_name, snapshot_date from {{ ref('mart_daily_role_skills') }}
where posting_count < 1 or role_posting_count < 1
    or posting_count > role_posting_count or skill_share < 0 or skill_share > 1
