"""Run Terraform using local .env credentials, never CLI arguments containing tokens."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv

from sea_it_jobs.config import check_connection, warehouse_id, workspace_client

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    load_dotenv(ROOT / ".env", override=False)
    check_connection()
    executable = shutil.which("terraform")
    if not executable:
        local = ROOT / "artifacts/tools/terraform.exe"
        if not local.is_file():
            raise SystemExit("Install Terraform >=1.9 and put it on PATH")
        executable = str(local)
    environment = os.environ.copy()
    # Terraform uses the same OAuth session as the SDK, with an ephemeral bearer token.
    client = workspace_client()
    authorization = client.config.authenticate().get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise SystemExit("Terraform deployment requires bearer authentication")
    environment["DATABRICKS_HOST"] = client.config.host
    environment["DATABRICKS_TOKEN"] = authorization.removeprefix("Bearer ")
    environment["DATABRICKS_AUTH_TYPE"] = "pat"
    environment.update(
        TF_VAR_catalog=os.getenv("DATABRICKS_CATALOG", "workspace"),
        TF_VAR_schema_prefix=os.getenv("SCHEMA_PREFIX", "vn_jobs"),
        TF_VAR_warehouse_id=warehouse_id(),
    )
    base = [executable, f"-chdir={ROOT / 'infra/terraform'}"]
    subprocess.run(base + ["init", "-lockfile=readonly"], env=environment, check=True)
    plan = ROOT / "artifacts/deployment.tfplan"
    plan.parent.mkdir(exist_ok=True)
    subprocess.run(base + ["plan", f"-out={plan}"], env=environment, check=True)
    if args.apply:
        subprocess.run(base + ["apply", str(plan)], env=environment, check=True)
        subprocess.run(base + ["output"], env=environment, check=True)


if __name__ == "__main__":
    main()
