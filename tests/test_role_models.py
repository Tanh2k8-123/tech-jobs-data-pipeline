import json
from datetime import UTC, datetime, time, timedelta

import pyarrow as pa
import pytest
from sql_harness import build_models
from test_models import observations

ROLE_CASES = [
    ("Senior Data Engineer (Python, Backend, AI)", "Data Engineer"),
    ("Lead Data Engineer (Azure / AWS / GCP)", "Data Engineer"),
    ("(Middle, Senior) Full-Stack Developer (Java, Go)", "Fullstack Developer"),
    ("[All Level] BackEnd Engineer (Java, Springboot)", "Backend Developer"),
    ("Senior Front-End Developer (Backend, Java)", "Frontend Developer"),
    ("Senior Ruby on Rails Developer (AWS, Backend)", "Software Developer"),
    ("Data Business Analyst (SQL)", "Business Analyst"),
    ("Senior Data Scientist - AI", "Data Scientist"),
    ("AI Software Engineer (Python, Go)", "AI / ML Engineer"),
    ("Agentic Engineer (Python, Backend)", "AI / ML Engineer"),
    ("Chuyên gia Quản trị hạ tầng (NETWORK & SECURITY)", "DevOps / Infrastructure"),
    ("Junior Mobile Developer (Java)", "Mobile Developer"),
    ("Security Operations Engineer", "Security Engineer"),
    ("Fullstack / Backend Engineer", "Fullstack Developer"),
    ("Maintenance Engineer", "Other"),
    ("HR Recruiter", "Other"),
]


@pytest.fixture(scope="module")
def role_database():
    raw, ledger = observations()
    base = raw.to_pylist()[0]
    rows = [
        {**base, "source_job_id": str(i), "title": title} for i, (title, _) in enumerate(ROLE_CASES)
    ]
    run = {**ledger.to_pylist()[0], "row_count": str(len(rows))}
    database = build_models(pa.Table.from_pylist(rows), pa.Table.from_pylist([run]))
    yield database
    database.close()


@pytest.mark.parametrize(("identity", "case"), list(enumerate(ROLE_CASES)))
def test_title_rules_use_roles_instead_of_skill_parentheses(role_database, identity, case):
    assert (
        role_database.execute(
            "SELECT role_family FROM fct_job_postings WHERE source_job_id=?", [str(identity)]
        ).fetchone()[0]
        == case[1]
    )


def test_multiple_explicit_roles_are_flagged(role_database):
    family, status, matches = role_database.execute(
        "SELECT role_family,role_classification,primary_role_matches "
        "FROM fct_job_daily_snapshots WHERE source_job_id='13'"
    ).fetchone()
    assert family == "Fullstack Developer"
    assert status == "multiple_primary_matches"
    assert matches == 2


def test_role_tags_are_excluded_and_equivalent_skills_are_deduplicated():
    raw, ledger = observations()
    base = raw.to_pylist()[0]
    row = {
        **base,
        "title": "Data Engineer",
        "skills_json": json.dumps(["Data Engineer", "Python", "python", "golang", "Go"]),
    }
    run = {**ledger.to_pylist()[0], "row_count": "1"}
    with build_models(pa.Table.from_pylist([row]), pa.Table.from_pylist([run])) as db:
        assert db.execute(
            "SELECT skill_name,posting_count,role_posting_count FROM mart_daily_role_skills "
            "ORDER BY skill_name"
        ).fetchall() == [("Go", 1, 1), ("Python", 1, 1)]


def test_daily_models_use_last_complete_batch_and_historical_skills():
    raw, _ = observations()
    base = raw.to_pylist()[0]
    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    specs = [
        ("early", yesterday, 10, "gone", "Data Analyst", ["Excel"], "old_company"),
        ("day1", yesterday, 12, "one", "Data Engineer", ["Python", "SQL", "python"], "old_company"),
        ("day2", today, 0, "one", "AI Engineer", ["Python", "PyTorch"], "new_company"),
    ]
    rows, runs = [], []
    for run_id, day, hour, identity, title, skills, company in specs:
        timestamp = datetime.combine(day, time(hour), UTC).isoformat()
        rows.append(
            {
                **base,
                "run_id": run_id,
                "source_job_id": identity,
                "title": title,
                "snapshot_date": day.isoformat(),
                "ingested_at": timestamp,
                "first_observed_at": timestamp,
                "company_id": company,
                "skills_json": json.dumps(skills),
            }
        )
        runs.append(
            {
                "source": "itviec",
                "run_id": run_id,
                "input_path": "unused",
                "parquet_sha256": "unused",
                "snapshot_date": day.isoformat(),
                "completed_at": timestamp,
                "row_count": "1",
            }
        )
    with build_models(pa.Table.from_pylist(rows), pa.Table.from_pylist(runs)) as db:
        assert db.execute("SELECT count(*) FROM fct_job_daily_snapshots").fetchone()[0] == 2
        assert (
            db.execute(
                "SELECT count(*) FROM fct_job_daily_snapshots WHERE source_job_id='gone'"
            ).fetchone()[0]
            == 0
        )
        counts = db.execute(
            "SELECT snapshot_date,role_family,posting_count "
            "FROM mart_daily_role_demand WHERE posting_count > 0 "
            "ORDER BY snapshot_date"
        ).fetchall()
        assert counts == [(yesterday, "Data Engineer", 1), (today, "AI / ML Engineer", 1)]
        assert db.execute(
            "SELECT posting_count,skill_share FROM mart_daily_role_skills "
            "WHERE snapshot_date=? AND skill_name='SQL'",
            [yesterday],
        ).fetchone() == (1, 1)
        assert (
            db.execute(
                "SELECT count(*) FROM mart_daily_role_skills "
                "WHERE snapshot_date=? AND skill_name='SQL'",
                [today],
            ).fetchone()[0]
            == 0
        )
        assert (
            db.execute("SELECT count(*) FROM dim_skills WHERE skill_name='SQL'").fetchone()[0] == 1
        )
        assert db.execute("SELECT count(*) FROM dim_companies").fetchone()[0] == 2
