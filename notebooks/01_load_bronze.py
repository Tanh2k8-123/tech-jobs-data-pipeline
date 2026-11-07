# Databricks notebook source
# ruff: noqa: F821
import hashlib
import json
import re

from delta.tables import DeltaTable
from pyspark.sql import functions as F

dbutils.widgets.text("input_path", "")
dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema_prefix", "vn_jobs")
input_path = dbutils.widgets.get("input_path").rstrip("/")
catalog = dbutils.widgets.get("catalog")
prefix = dbutils.widgets.get("schema_prefix")
for identifier in (catalog, prefix):
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", identifier):
        raise ValueError("Invalid catalog/schema identifier")
root = f"/Volumes/{catalog}/{prefix}_bronze/raw_files/itviec/"
if not input_path.startswith(root) or ".." in input_path.split("/"):
    raise ValueError("input_path must point into the project's managed raw Volume")
with open(input_path + "/manifest.json", encoding="utf-8") as stream:
    manifest = json.load(stream)
if manifest.get("complete") is not True or manifest.get("schema_version") != 1:
    raise ValueError("Only complete version-1 runs can enter Bronze")
digest = hashlib.sha256()
with open(input_path + "/jobs.parquet", "rb") as stream:
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
if digest.hexdigest() != manifest["parquet_sha256"]:
    raise ValueError("Raw Parquet checksum mismatch")

incoming = spark.read.parquet(input_path + "/jobs.parquet")
keys = ["source", "source_job_id", "run_id"]
if incoming.count() != manifest["row_count"] or manifest["row_count"] < 1:
    raise ValueError("Raw row count differs from the completed manifest")
if incoming.groupBy(keys).count().filter("count > 1").limit(1).count():
    raise ValueError("Duplicate observations in input")
invalid = incoming.filter(
    F.col("source_job_id").isNull()
    | (F.col("source") != manifest["source"])
    | (F.col("run_id") != manifest["run_id"])
    | (F.col("snapshot_date") != manifest["snapshot_date"])
)
if invalid.limit(1).count():
    raise ValueError("Input rows violate the manifest identity")

table = f"{catalog}.{prefix}_bronze.raw_it_job_observations"
if not spark.catalog.tableExists(table):
    incoming.limit(0).write.format("delta").saveAsTable(table)
existing = spark.table(table).alias("t").join(incoming.alias("s"), keys)
if existing.filter(F.col("t.payload_hash") != F.col("s.payload_hash")).limit(1).count():
    raise ValueError("Attempt to mutate an existing immutable observation")
condition = " AND ".join(f"t.{key} = s.{key}" for key in keys)
DeltaTable.forName(spark, table).alias("t").merge(
    incoming.alias("s"), condition
).whenNotMatchedInsertAll().execute()

# Write the run ledger LAST. Orphan observations from a failed task stay invisible to Silver.
run_row = {
    key: str(manifest[key])
    for key in ("source", "snapshot_date", "run_id", "row_count", "completed_at", "parquet_sha256")
}
run_row["input_path"] = input_path
runs = spark.createDataFrame([run_row])
run_table = f"{catalog}.{prefix}_bronze.ingestion_runs"
if not spark.catalog.tableExists(run_table):
    runs.limit(0).write.format("delta").saveAsTable(run_table)
DeltaTable.forName(spark, run_table).alias("t").merge(
    runs.alias("s"), "t.run_id = s.run_id"
).whenNotMatchedInsertAll().execute()
print(
    json.dumps(
        {"event": "bronze_complete", "run_id": manifest["run_id"], "rows": manifest["row_count"]}
    )
)
