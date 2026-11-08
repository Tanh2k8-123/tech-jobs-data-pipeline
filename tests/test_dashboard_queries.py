import json

import pyarrow as pa
import pytest
from sql_harness import ROOT, build_models, lower
from test_models import observations


@pytest.fixture(scope="module")
def query_database():
    raw, ledger = observations()
    rows = raw.to_pylist()
    for row in rows:
        row["title"] = "Data Engineer"
        if row["run_id"] == "r2" and row["source_job_id"] == "upper":
            row["skills_json"] = json.dumps(["Python"])
    rows.append(
        {
            **rows[-1],
            "source_job_id": "back",
            "title": "Backend Engineer",
            "skills_json": json.dumps(["Go"]),
        }
    )
    runs = ledger.to_pylist()
    runs[-1]["row_count"] = "3"
    database = build_models(pa.Table.from_pylist(rows), pa.Table.from_pylist(runs))
    yield database
    database.close()


def execute(db, name, role):
    sql = (ROOT / "dashboards/queries" / f"{name}.sql").read_text(encoding="utf-8")
    sql = sql.replace("${catalog}.${prefix}_gold.", "").replace("${catalog}.${prefix}_silver.", "")
    sql = sql.replace(":role_family", "'" + role.replace("'", "''") + "'")
    cursor = db.execute(lower(sql))
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row, strict=True)) for row in cursor.fetchall()]


@pytest.mark.parametrize(
    ("role", "posts"),
    [("All roles", 3), ("Data Engineer", 2), ("Backend Developer", 1), ("Data Analyst", 0)],
)
def test_selected_role_counts_and_denominators(query_database, role, posts):
    summary = execute(query_database, "role_summary", role)[0]
    assert summary["posting_count"] == posts
    assert summary["collected_days"] == 2
    assert summary["snapshot_date"] is not None
    rows = execute(query_database, "role_skills", role)
    assert all(row["role_posting_count"] == posts for row in rows)
    assert all(0 <= row["skill_share_pct"] <= 100 for row in rows)
    if role == "Data Engineer":
        sql = next(row for row in rows if row["skill_name"] == "SQL")
        assert sql["posting_count"] == 1
        assert sql["skill_share_pct"] == 50.0


def test_skill_trends_preserve_past_skills(query_database):
    trend = execute(query_database, "skill_trend", "Data Engineer")
    sql = sorted((r for r in trend if r["skill_name"] == "SQL"), key=lambda r: r["snapshot_date"])
    assert [row["skill_share_pct"] for row in sql] == [100.0, 50.0]
    details = execute(query_database, "role_skill_details", "Data Engineer")
    assert {row["role_family"] for row in details} == {"Data Engineer"}
    assert all(row["role_posting_count"] == 2 for row in details)


def test_overview_and_selected_role_trends(query_database):
    assert len(execute(query_database, "role_ranking", "All roles")) == 2
    rows = execute(query_database, "role_trend", "Backend Developer")
    assert {row["role_family"] for row in rows} == {"Backend Developer"}
    assert sorted(row["posting_count"] for row in rows) == [0, 1]
