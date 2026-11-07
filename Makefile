.PHONY: setup check extract pipeline-run replay infra-init infra-plan infra-up
setup:
	uv sync --locked --extra dev
check:
	uv run ruff check .
	uv run pytest -q
	uv run dbt parse --project-dir dbt --profiles-dir dbt --no-partial-parse
extract:
	uv run it-jobs extract
pipeline-run:
	uv run it-jobs run --job-id $(JOB_ID)
replay:
	uv run it-jobs replay --input "$(RUN_PATH)" --job-id $(JOB_ID)
infra-init:
	terraform -chdir=infra/terraform init
infra-plan:
	terraform -chdir=infra/terraform plan
infra-up:
	terraform -chdir=infra/terraform apply
