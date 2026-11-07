"""Configure this pipeline's GitHub repository without writing secret values to disk."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from sea_it_jobs.config import warehouse_id, workspace_client

ROOT = Path(__file__).resolve().parents[1]


def gh(arguments, value=None):
    executable = shutil.which("gh")
    command = [executable] if executable else ["wsl.exe", "--exec", "/usr/bin/gh"]
    result = subprocess.run(
        command + arguments, input=value, capture_output=True, text=True, timeout=45
    )
    if result.returncode:
        # Keep stderr private: a failed secret-setting operation must not echo input.
        raise RuntimeError("GitHub CLI failed: " + " ".join(arguments[:2]))
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args()
    load_dotenv(ROOT / ".env", override=False)
    metadata = json.loads(gh(["api", "repos/" + args.repo]))
    if not metadata.get("permissions", {}).get("push"):
        raise SystemExit("No push permission for the requested repository")
    client = workspace_client()
    warehouse_id(client)
    existing = {
        secret["name"]
        for secret in json.loads(gh(["secret", "list", "--repo", args.repo, "--json", "name"]))
    }
    expiry = None
    if "DATABRICKS_TOKEN" not in existing:
        created = client.tokens.create(
            lifetime_seconds=90 * 86400,
            comment="GitHub Actions: " + args.repo + " (Vietnam IT jobs)",
        )
        try:
            gh(["secret", "set", "DATABRICKS_TOKEN", "--repo", args.repo], created.token_value)
        except Exception:
            client.tokens.delete(created.token_info.token_id)
            raise
        expiry = datetime.fromtimestamp(created.token_info.expiry_time / 1000, UTC).isoformat()
    for name, value in {
        "DATABRICKS_HOST": client.config.host,
        "DATABRICKS_HTTP_PATH": os.environ["DATABRICKS_HTTP_PATH"],
    }.items():
        gh(["secret", "set", name, "--repo", args.repo], value)
    for name, value in {
        "PIPELINE_JOB_ID": args.job_id,
        "DATABRICKS_CATALOG": os.getenv("DATABRICKS_CATALOG", "workspace"),
        "SCHEMA_PREFIX": os.getenv("SCHEMA_PREFIX", "vn_jobs"),
        "ENABLE_DAILY_PIPELINE": "false",
    }.items():
        gh(["variable", "set", name, "--repo", args.repo, "--body", value])
    print(
        json.dumps(
            {
                "repository": args.repo,
                "secrets_configured": True,
                "daily_schedule": "disabled_until_workflow_verification",
                "created_token_expires_at": expiry,
            }
        )
    )


if __name__ == "__main__":
    main()
