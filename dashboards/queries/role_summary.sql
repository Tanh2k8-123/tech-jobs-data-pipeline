with latest as (
    select max(snapshot_date) as snapshot_date
    from ${catalog}.${prefix}_gold.fct_job_daily_snapshots
), eligible_tags as (
    select b.snapshot_sk, b.skill_sk
    from ${catalog}.${prefix}_gold.bridge_job_snapshot_skills b
    inner join ${catalog}.${prefix}_gold.dim_skills d on b.skill_sk = d.skill_sk
    left join ${catalog}.${prefix}_silver.role_tag_labels r on lower(d.skill_name) = r.skill_name
    where r.skill_name is null
)
select :role_family as selected_role,
    count(distinct f.job_sk) as posting_count,
    count(distinct f.company_sk) as company_count,
    count(distinct t.skill_sk) as skill_count,
    (select snapshot_date from latest) as snapshot_date,
    (select max(collected_at) from ${catalog}.${prefix}_gold.fct_job_daily_snapshots
     where snapshot_date = (select snapshot_date from latest)) as data_collected_at,
    (select count(distinct snapshot_date)
     from ${catalog}.${prefix}_gold.fct_job_daily_snapshots) as collected_days,
    count(distinct case when f.role_classification = 'unclassified' then f.job_sk end)
        as unclassified_posts,
    count(distinct case when f.role_classification = 'multiple_primary_matches' then f.job_sk end)
        as multiple_role_titles
from ${catalog}.${prefix}_gold.fct_job_daily_snapshots f
inner join latest l on f.snapshot_date = l.snapshot_date
left join eligible_tags t on f.snapshot_sk = t.snapshot_sk
where :role_family = 'All roles' or f.role_family = :role_family
