import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq

from sea_it_jobs.http import HttpClient
from sea_it_jobs.salary import parse_salary
from sea_it_jobs.sources.itviec import extract

LOG = logging.getLogger(__name__)


def vietnam_today():
    return datetime.now(timezone(timedelta(hours=7))).date().isoformat()


def collect(root: Path, *, delay: float = 1.0, max_pages: int = 100):
    started = datetime.now(UTC)
    snapshot_date = vietnam_today()
    run_id = started.strftime("%Y%m%dT%H%M%S") + "_" + uuid4().hex[:12]
    path = root / snapshot_date / run_id
    path.mkdir(parents=True, exist_ok=False)
    client = HttpClient(delay)
    jobs, summary = extract(client, snapshot_date, max_pages)
    response = client.get("https://open.er-api.com/v6/latest/USD")
    fx = response.json()
    if fx.get("result") != "success" or fx.get("base_code") != "USD":
        raise ValueError("FX provider returned an invalid response")
    fx_time = datetime.fromtimestamp(fx["time_last_update_unix"], UTC)
    age = (datetime.now(UTC) - fx_time).total_seconds()
    if age < -300 or age > 48 * 3600:
        raise ValueError("FX data is older than 48 hours or in the future")
    vnd_per_usd = float(fx["rates"]["VND"])
    if not 10000 < vnd_per_usd < 100000:
        raise ValueError("VND/USD rate outside expected validation range")
    finished = datetime.now(UTC)
    if vietnam_today() != snapshot_date:
        raise ValueError("Extraction crossed the Vietnam date boundary; restart")
    rows = []
    seen = set()
    for job in jobs:
        key = (job["source"], job["source_job_id"])
        if key in seen:
            raise ValueError("Duplicate source identity after extraction")
        seen.add(key)
        payload = json.dumps(job, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        row = {
            key: job.get(key)
            for key in (
                "source",
                "source_job_id",
                "job_url",
                "company_id",
                "company_name",
                "title",
                "salary_text",
                "salary_basis",
                "posted_date",
                "valid_through",
            )
        }
        row.update(
            parse_salary(job["salary_text"], job["salary_period"], job["salary_currency_hint"])
        )
        row.update(
            locations_json=json.dumps(job["locations"], ensure_ascii=False),
            skills_json=json.dumps(job["skills"], ensure_ascii=False),
            snapshot_date=snapshot_date,
            ingested_at=finished.isoformat(),
            first_observed_at=started.isoformat(),
            run_id=run_id,
            payload_hash=hashlib.sha256(payload.encode()).hexdigest(),
            raw_payload_json=payload,
            fx_vnd_per_usd=vnd_per_usd,
            fx_rate_at=fx_time.isoformat(),
            fx_provider="https://www.exchangerate-api.com",
        )
        rows.append(row)
    numeric = {"salary_min_native", "salary_max_native", "fx_vnd_per_usd"}
    schema = pa.schema(
        [(column, pa.float64() if column in numeric else pa.string()) for column in rows[0]]
    )
    pq.write_table(
        pa.Table.from_pylist(rows, schema=schema), path / "jobs.parquet", compression="zstd"
    )
    (path / "fx.json").write_text(json.dumps(fx, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "complete": True,
        "source": "itviec",
        "snapshot_date": snapshot_date,
        "run_id": run_id,
        "row_count": len(rows),
        "started_at": started.isoformat(),
        "completed_at": finished.isoformat(),
        "parquet_sha256": hashlib.sha256((path / "jobs.parquet").read_bytes()).hexdigest(),
        "extraction": summary,
        "parser_version": "1",
    }
    (path / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    LOG.info("extraction_complete rows=%s run_id=%s path=%s", len(rows), run_id, path)
    return path
