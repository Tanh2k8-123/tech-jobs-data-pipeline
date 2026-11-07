import argparse
import logging
import os
from pathlib import Path

import requests
from databricks.sdk.errors import DatabricksError
from dotenv import load_dotenv

from sea_it_jobs.cloud import run_pipeline, upload_and_run
from sea_it_jobs.config import check_connection
from sea_it_jobs.ingestion import collect


def main():
    load_dotenv(Path.cwd() / ".env", override=False)
    parser = argparse.ArgumentParser(description="Real-source Vietnam IT jobs pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    for name in ("extract", "run", "replay"):
        command = commands.add_parser(name)
        if name == "extract":
            command.add_argument("--output", type=Path, default=Path("artifacts/landing"))
            command.add_argument("--request-interval", type=float, default=1.0)
            command.add_argument("--max-pages", type=int, default=100)
        elif name == "replay":
            command.add_argument("--input", type=Path, required=True)
        if name != "extract":
            command.add_argument("--catalog", default=os.getenv("DATABRICKS_CATALOG", "workspace"))
            command.add_argument("--schema-prefix", default=os.getenv("SCHEMA_PREFIX", "vn_jobs"))
            command.add_argument("--job-id", type=int, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        if args.command == "check":
            check_connection()
            return 0
        if args.command == "run":
            check_connection()
            run_pipeline(args.catalog, args.schema_prefix, args.job_id)
        elif args.command == "replay":
            upload_and_run(args.input, args.catalog, args.schema_prefix, args.job_id)
        else:
            collect(args.output, delay=args.request_interval, max_pages=args.max_pages)
    except (requests.RequestException, DatabricksError) as error:
        logging.error(
            "Remote operation failed: %s; no fallback data was published", type(error).__name__
        )
        return 1
    except (ValueError, OSError, KeyError) as error:
        logging.error("Pipeline failed: %s", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
