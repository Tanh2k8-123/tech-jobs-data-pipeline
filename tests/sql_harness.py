"""Execute the project SQL in an isolated test DB, lowering Spark syntax with SQLGlot.

This verifies business semantics without a demo command or production DuckDB path.
Databricks runtime/integration validation remains a separate cloud check.
"""

import re
from pathlib import Path

import duckdb
import pyarrow as pa
import sqlglot
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]


def render(path):
    macro = (ROOT / "dbt/macros/schema.sql").read_text(encoding="utf-8")
    return (
        Environment(undefined=StrictUndefined)
        .from_string(macro + path.read_text(encoding="utf-8"))
        .render(
            ref=lambda name: name,
            source=lambda _, name: "bronze." + name,
            config=lambda **kwargs: "",
            var=lambda name: {"enable_liquid_clustering": False, "schema_prefix": "vn_jobs"}[name],
        )
    )


def lower(sql):
    # FROM_JSON exists on both engines but takes a JSON type description in DuckDB.
    sql = sql.replace("'array<string>'", "'[\"VARCHAR\"]'")
    return sqlglot.transpile(sql, read="databricks", write="duckdb", unsupported_level="RAISE")[0]


def build_models(observations: pa.Table, runs: pa.Table):
    connection = duckdb.connect()
    connection.execute("CREATE SCHEMA bronze")
    for name, table in (("raw_it_job_observations", observations), ("ingestion_runs", runs)):
        connection.register("input_data", table)
        connection.execute(f"CREATE TABLE bronze.{name} AS SELECT * FROM input_data")
        connection.unregister("input_data")
    built = set()
    for seed in (ROOT / "dbt/seeds").glob("*.csv"):
        connection.execute(f"CREATE TABLE {seed.stem} AS SELECT * FROM read_csv(?)", [str(seed)])
        built.add(seed.stem)
    pending = list((ROOT / "dbt/models").rglob("*.sql"))
    while pending:
        ready = [
            path
            for path in pending
            if set(re.findall(r"ref\('([^']+)'\)", path.read_text(encoding="utf-8"))) <= built
        ]
        if not ready:
            raise AssertionError("Unresolved model dependencies")
        for path in ready:
            connection.execute(f"CREATE TABLE {path.stem} AS {lower(render(path))}")
            built.add(path.stem)
            pending.remove(path)
    return connection
