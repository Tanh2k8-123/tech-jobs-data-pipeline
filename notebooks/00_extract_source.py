# Databricks notebook source
# ruff: noqa: F821, E402
dbutils.widgets.text("input_path", "")
dbutils.widgets.text("raw_root", "")
dbutils.widgets.text("source_root", "")
input_path = dbutils.widgets.get("input_path").rstrip("/")
raw_root = dbutils.widgets.get("raw_root").rstrip("/")
if input_path:
    if not input_path.startswith(raw_root + "/") or ".." in input_path.split("/"):
        raise ValueError("Replay input must be inside this project's raw Volume")
    dbutils.jobs.taskValues.set(key="raw_path", value=input_path)
    dbutils.notebook.exit("Reusing immutable source batch")

# COMMAND ----------
# MAGIC %pip install beautifulsoup4==4.15.0

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
source_root = dbutils.widgets.get("source_root")
raw_root = dbutils.widgets.get("raw_root")
if not source_root.startswith("/Workspace/") or not raw_root.startswith("/Volumes/"):
    raise ValueError("Expected a workspace package and managed Volume")
sys.path.insert(0, source_root)
from sea_it_jobs.ingestion import collect  # noqa: E402

path = collect(Path(raw_root))
dbutils.jobs.taskValues.set(key="raw_path", value=str(path))
print("Completed real source batch:", path.name)
