import hashlib
import json

import pytest

from sea_it_jobs.cloud import validate_run


def test_landing_checksum_prevents_tampered_replay(tmp_path):
    raw = tmp_path / "jobs.parquet"
    raw.write_bytes(b"original observation")
    manifest = {
        "schema_version": 1,
        "complete": True,
        "snapshot_date": "2026-11-07",
        "run_id": "run_1",
        "parquet_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert validate_run(tmp_path)["run_id"] == "run_1"
    raw.write_bytes(b"modified observation")
    with pytest.raises(ValueError, match="checksum"):
        validate_run(tmp_path)


def test_incomplete_run_cannot_be_uploaded(tmp_path):
    (tmp_path / "manifest.json").write_text('{"schema_version":1,"complete":false}')
    with pytest.raises(ValueError, match="Incomplete"):
        validate_run(tmp_path)
