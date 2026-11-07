locals {
  dbt_root = "${path.module}/../../dbt"
  dbt_files = toset([
    for file in fileset(local.dbt_root, "**") : file
    if can(regex("\\.(sql|yml|csv)$", file)) && !contains(["profiles.yml", ".user.yml"], file)
    && !can(regex("^(target|logs|dbt_packages)/", file))
  ])
  dbt_vars = jsonencode({
    catalog                  = var.catalog
    schema_prefix            = var.schema_prefix
    enable_liquid_clustering = var.enable_liquid_clustering
  })
}

resource "databricks_schema" "layer" {
  for_each      = toset(["bronze", "silver", "gold"])
  catalog_name  = var.catalog
  name          = "${var.schema_prefix}_${each.value}"
  comment       = "Vietnam IT jobs ${each.value} layer; managed by Terraform"
  force_destroy = false
}

resource "databricks_volume" "raw" {
  catalog_name = var.catalog
  schema_name  = databricks_schema.layer["bronze"].name
  name         = "raw_files"
  volume_type  = "MANAGED"
  comment      = "Immutable source observations, FX snapshots and completion manifests"
}

resource "databricks_directory" "project" {
  path = var.workspace_path
}

resource "databricks_notebook" "bronze" {
  path       = "${var.workspace_path}/01_load_bronze"
  language   = "PYTHON"
  source     = "${path.module}/../../notebooks/01_load_bronze.py"
  depends_on = [databricks_directory.project]
}

resource "databricks_workspace_file" "dbt" {
  for_each   = local.dbt_files
  path       = "${var.workspace_path}/dbt/${each.value}"
  source     = "${local.dbt_root}/${each.value}"
  depends_on = [databricks_directory.dbt]
}

resource "databricks_directory" "dbt" {
  for_each   = toset([for file in local.dbt_files : replace(dirname(file), "\\", "/")])
  path       = each.value == "." ? "${var.workspace_path}/dbt" : "${var.workspace_path}/dbt/${each.value}"
  depends_on = [databricks_directory.project]
}

resource "databricks_dashboard" "market" {
  display_name      = "Vietnam IT Job Market"
  warehouse_id      = var.warehouse_id
  parent_path       = var.workspace_path
  embed_credentials = false
  serialized_dashboard = templatefile("${path.module}/../../dashboards/market.lvdash.json.tftpl", {
    catalog = var.catalog
    prefix  = var.schema_prefix
  })
  depends_on = [databricks_directory.project]
}

resource "databricks_job" "pipeline" {
  name                = "Vietnam IT jobs - Bronze, dbt and dashboard"
  max_concurrent_runs = 1
  timeout_seconds     = 7200
  tags = {
    project       = "sea-it-jobs"
    schema_prefix = var.schema_prefix
  }
  queue { enabled = true }
  parameter {
    name    = "input_path"
    default = ""
  }
  environment {
    environment_key = "dbt"
    spec {
      environment_version = "2"
      dependencies        = ["dbt-databricks==1.13.0", "dbt-core==1.12.6"]
    }
  }
  task {
    task_key                  = "load_bronze"
    timeout_seconds           = 1800
    max_retries               = 2
    min_retry_interval_millis = 30000
    notebook_task {
      notebook_path = databricks_notebook.bronze.path
      base_parameters = {
        input_path    = "{{job.parameters.input_path}}"
        catalog       = var.catalog
        schema_prefix = var.schema_prefix
      }
    }
  }
  task {
    task_key        = "dbt_build"
    environment_key = "dbt"
    timeout_seconds = 3600
    max_retries     = 1
    depends_on { task_key = "load_bronze" }
    dbt_task {
      source            = "WORKSPACE"
      project_directory = "/Workspace${var.workspace_path}/dbt"
      warehouse_id      = var.warehouse_id
      catalog           = var.catalog
      schema            = databricks_schema.layer["silver"].name
      commands          = ["dbt build --vars '${local.dbt_vars}'"]
    }
  }
  task {
    task_key        = "refresh_dashboard"
    timeout_seconds = 900
    depends_on { task_key = "dbt_build" }
    dashboard_task {
      dashboard_id = databricks_dashboard.market.id
      warehouse_id = var.warehouse_id
    }
  }
  depends_on = [databricks_workspace_file.dbt, databricks_volume.raw]
}
