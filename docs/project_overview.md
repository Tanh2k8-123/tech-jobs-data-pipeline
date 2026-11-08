# Project overview

This project follows the path from public job pages to a dashboard. It is a way to practice data collection, SQL modeling, testing, and cloud deployment in one project.

It collects ITviec posts each day and reports role counts and skill mentions by role. The current scope is Vietnam. Other sources and Singapore are possible future additions.

## Main choices

- Daily batches are enough for these reports.
- Raw files are saved so the same input can be processed again.
- Bronze keeps each observation. Gold keeps one current record per post.
- dbt keeps the SQL models and tests together.
- Terraform makes the workspace setup repeatable.

The hardest parts were handling source changes, choosing what each table row means, and getting the cloud tasks to work together.

## Current limits

Many salaries are hidden. The dataset is small, so this project does not prove a performance advantage for Spark or clustering. Gold is rebuilt each run.

Possible next steps are adding another verified source, measuring query performance, and using incremental models if the data grows.

Start with the [README](../README.md) or [learning guide](portfolio_learning_guide.md).
