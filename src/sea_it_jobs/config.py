import json
import os
import re
import subprocess
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient


class WslCredentials:
    """Reuse a user's WSL OAuth login; access tokens never enter files or logs."""

    def __init__(self, profile):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", profile):
            raise ValueError("Invalid WSL Databricks profile name")
        self.profile = profile
        self.token = None
        self.refresh_at = 0

    def auth_type(self):
        return "wsl-cli"

    def __call__(self, config):
        def headers():
            if time.monotonic() >= self.refresh_at:
                response = subprocess.run(
                    [
                        "wsl.exe",
                        "--exec",
                        "/usr/local/bin/databricks",
                        "auth",
                        "token",
                        "--profile",
                        self.profile,
                        "--timeout",
                        "20s",
                        "--output",
                        "json",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if response.returncode:
                    raise ValueError(
                        "WSL OAuth session unavailable; run databricks auth login in WSL"
                    )
                token = json.loads(response.stdout)
                self.token = token["access_token"]
                self.refresh_at = time.monotonic() + min(300, max(1, token["expires_in"] - 60))
            return {"Authorization": f"Bearer {self.token}"}

        return headers


def workspace_client():
    profile = os.getenv("DATABRICKS_WSL_PROFILE")
    if profile and os.name == "nt" and not os.getenv("DATABRICKS_TOKEN"):
        return WorkspaceClient(
            host=os.getenv("DATABRICKS_HOST"), credentials_strategy=WslCredentials(profile)
        )
    return WorkspaceClient(profile=profile if profile else None)


def warehouse_id(client=None):
    if not os.getenv("DATABRICKS_HTTP_PATH") and client is not None:
        warehouses = list(client.warehouses.list())
        if len(warehouses) != 1:
            raise ValueError("Set DATABRICKS_HTTP_PATH to select one SQL warehouse")
        os.environ["DATABRICKS_HTTP_PATH"] = "/sql/1.0/warehouses/" + warehouses[0].id
        path = Path.cwd() / ".env"
        if path.exists() and "DATABRICKS_HTTP_PATH=" not in path.read_text(encoding="utf-8"):
            with path.open("a", encoding="utf-8") as stream:
                stream.write("DATABRICKS_HTTP_PATH=" + os.environ["DATABRICKS_HTTP_PATH"] + "\n")
    match = re.fullmatch(
        r"/sql/1\.0/warehouses/([a-zA-Z0-9-]+)", os.getenv("DATABRICKS_HTTP_PATH", "")
    )
    if not match:
        raise ValueError("DATABRICKS_HTTP_PATH must be /sql/1.0/warehouses/<id>")
    return match[1]


def check_connection():
    client = workspace_client()
    client.current_user.me()
    warehouse = client.warehouses.get(warehouse_id(client))
    catalog = os.getenv("DATABRICKS_CATALOG", "workspace")
    client.catalogs.get(catalog)
    response = client.statement_execution.execute_statement(
        statement="SELECT 1 AS connection_ok",
        warehouse_id=warehouse_id(),
        catalog=catalog,
        wait_timeout="50s",
    )
    deadline = time.monotonic() + 120
    while response.status.state.value in {"PENDING", "RUNNING"} and time.monotonic() < deadline:
        time.sleep(2)
        response = client.statement_execution.get_statement(response.statement_id)
    if response.status.state.value != "SUCCEEDED":
        raise ValueError("SQL warehouse connection query did not succeed")
    print(
        json.dumps(
            {
                "workspace": "connected",
                "warehouse": "query_succeeded",
                "warehouse_state": warehouse.state.value,
                "catalog": catalog,
            }
        )
    )
