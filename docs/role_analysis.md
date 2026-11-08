# Role and skill analysis

The dashboard compares role families and the skills mentioned in their postings. It uses source observations, not an estimate of every open job in Vietnam.

## Role labels

`dbt/seeds/role_rules.csv` maps title patterns to one primary role family. Titles are lowercased, Vietnamese accents and common separators are normalized, and leading level labels are removed.

Rules first use the title before skill parentheses. If no rule matches there, they use the full title. This keeps `Data Engineer (Python, Backend)` in Data Engineer instead of Backend Developer. Lower priority numbers win when more than one rule matches.

The raw title, winning rule ID, match method, and count of specific primary matches are retained. Generic titles, multiple matches, and `Other` need review. Coverage is not measured classification accuracy. Changing rules reclassifies history using the new rules.

## Daily history

`fct_job_daily_snapshots` keeps posts from the last completed source batch for each collected day. It uses that observation's title and skills, not today's skill bridge applied to old data.

Missing collection days are absent, not zero. A role gets zero only when a successful snapshot exists and contains no posts for that role. Counts describe observed stock, not newly published jobs. The first collection is a baseline, not a spike in new hiring.

## Skill share

`mart_daily_role_skills` counts distinct posts mentioning each skill. It excludes exact role-name tags listed in `role_tag_labels.csv`; all tags remain in the underlying bridges.

```text
skill share = posts mentioning the skill / all observed posts for the selected role
```

For example, 10 of 20 posts means 50%, not 10 divided by the number of skill tags. Shares can add to more than 100% because one post has several skills. Tags may include languages or practices and are not a complete list of mandatory requirements.

## Dashboard

The role ranking always shows all roles in the latest daily snapshot. The role selector controls the KPIs, role trend, skill ranking, skill trend, and detail table. Default trends show six role families and five skills; a selected role narrows the analysis.

Snapshot details show the available days, collection timestamp, and title-label issues. A short history is not enough to claim a long-term hiring trend. Daily facts have clustering configured on `snapshot_date` and `role_family`, which match the report filters; performance gains are not claimed for this small dataset.
