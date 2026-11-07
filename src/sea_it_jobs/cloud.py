import hashlib
import json
import logging
import re
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from databricks.sdk.errors import NotFound

from sea_it_jobs.config import workspace_client

LOG = logging.getLogger(__name__)


def validate_run(path: Path):
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("complete") is not True:
        raise ValueError("Incomplete or unsupported run manifest")
    digest = hashlib.sha256((path / "jobs.parquet").read_bytes()).hexdigest()
    if digest != manifest["parquet_sha256"]:
        raise ValueError("Parquet checksum does not match manifest")
    for key in ("snapshot_date", "run_id"):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", manifest[key]):
            raise ValueError("Invalid manifest path component")
    return manifest


def run_pipeline(catalog: str, prefix: str, job_id: int, input_path: str = ""):
    for identifier in (catalog, prefix):
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", identifier):
            raise ValueError("Catalog and schema prefix must be simple SQL identifiers")
    client = workspace_client()
    job = client.jobs.get(job_id)
    tags = job.settings.tags if job.settings else {}
    if (
        not tags
        or tags.get("project") != "sea-it-jobs"
        or tags.get("schema_prefix") != prefix
        or tags.get("catalog") != catalog
    ):
        raise ValueError("Job project/schema tags do not match requested destination")
    LOG.info("databricks_job_submitted job_id=%s", job_id)
    waiter = client.jobs.run_now(
        job_id=job_id,
        job_parameters={"input_path": input_path},
        idempotency_token=uuid4().hex,
    )
    LOG.info("databricks_run_started run_id=%s", waiter.response.run_id)
    result = waiter.result(timeout=timedelta(hours=2))
    LOG.info("databricks_job_succeeded run_id=%s", result.run_id)


def upload_and_run(path: Path, catalog: str, prefix: str, job_id: int):
    manifest = validate_run(path)
    for identifier in (catalog, prefix):
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", identifier):
            raise ValueError("Catalog and schema prefix must be simple SQL identifiers")
    client = workspace_client()
    destination = (
        f"/Volumes/{catalog}/{prefix}_bronze/raw_files/itviec/"
        f"{manifest['snapshot_date']}/{manifest['run_id']}"
    )
    client.files.create_directory(destination)
    for name in ("jobs.parquet", "fx.json", "manifest.json"):
        remote = f"{destination}/{name}"
        local = path / name
        try:
            existing = client.files.download(remote)
        except NotFound:
            client.files.upload_from(remote, str(local), overwrite=False)
        else:
            with existing.contents as stream:
                if (
                    hashlib.sha256(stream.read()).digest()
                    != hashlib.sha256(local.read_bytes()).digest()
                ):
                    raise ValueError("Immutable cloud path already has different content")
    run_pipeline(catalog, prefix, job_id, destination)
