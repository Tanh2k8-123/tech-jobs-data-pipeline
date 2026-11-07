import json
from datetime import UTC, datetime, timedelta

import pyarrow as pa
from sql_harness import ROOT, build_models, lower, render

from sea_it_jobs.salary import parse_salary


def observations():
    now = datetime.now(UTC)
    rows = []
    for run, offset, jobs in [("r1", -1, ["one", "gone"]), ("r2", 0, ["one", "upper"])]:
        observed = now + timedelta(days=offset)
        for identity in jobs:
            upper = identity == "upper"
            row = {
                "source": "itviec",
                "source_job_id": identity,
                "company_id": "company",
                "company_name": "Company",
                "title": identity,
                "job_url": "https://itviec.com/it-jobs/" + identity,
                "salary_text": "Up to $3000" if upper else "$1000 - $1800",
                "salary_basis": "unknown",
                "fx_vnd_per_usd": 25000.0,
                "fx_rate_at": now.isoformat(),
                "fx_provider": "test-only-provider",
                "skills_json": json.dumps(["Python", "python", "SQL"]),
                "locations_json": json.dumps(["Hà Nội", "Ho Chi Minh"]),
                "posted_date": (now - timedelta(days=5)).date().isoformat(),
                "snapshot_date": observed.date().isoformat(),
                "ingested_at": observed.isoformat(),
                "first_observed_at": observed.isoformat(),
                "run_id": run,
                "payload_hash": identity + run,
            }
            row.update(parse_salary(row["salary_text"], "month"))
            rows.append(row)
    runs = [
        {
            "source": "itviec",
            "run_id": run,
            "input_path": "unused",
            "parquet_sha256": "unused",
            "snapshot_date": (now + timedelta(days=offset)).date(),
            "completed_at": now + timedelta(days=offset),
            "row_count": "2",
        }
        for run, offset in [("r1", -1), ("r2", 0)]
    ]
    return pa.Table.from_pylist(rows), pa.Table.from_pylist(runs)


def test_models_preserve_history_and_correct_analytics():
    with build_models(*observations()) as db:
        assert db.execute("SELECT count(*) FROM stg_job_history").fetchone()[0] == 4
        assert db.execute("SELECT count(*) FROM fct_job_postings").fetchone()[0] == 3
        assert (
            db.execute(
                "SELECT count(*) FROM fct_job_postings WHERE observed_in_latest_snapshot"
            ).fetchone()[0]
            == 2
        )
        assert db.execute("SELECT count(*) FROM bridge_job_skills").fetchone()[0] == 6
        salary = db.execute(
            "SELECT min_salary_usd,max_salary_usd,avg_salary_usd "
            "FROM fct_job_postings WHERE source_job_id='upper'"
        ).fetchone()
        assert salary == (None, 3000.0, None)
        demand = db.execute(
            "SELECT job_count,salary_sample_count,avg_salary_usd,salary_coverage "
            "FROM mart_skill_demand WHERE skill_name='Python'"
        ).fetchone()
        assert demand == (2, 1, 1400.0, 0.5)
        assert db.execute("SELECT count(*) FROM bridge_job_cities").fetchone()[0] == 6
        assert db.execute("SELECT sum(job_count) FROM mart_daily_city_jobs").fetchone()[0] == 6
        first_seen, last_seen = db.execute(
            "SELECT first_seen_at,last_seen_at FROM fct_job_postings WHERE source_job_id='one'"
        ).fetchone()
        assert last_seen > first_seen
        for path in (ROOT / "dbt/tests").glob("assert_*.sql"):
            assert db.execute(lower(render(path))).fetchall() == [], path.name
