output "job_id" { value = databricks_job.pipeline.id }
output "job_url" { value = databricks_job.pipeline.url }
output "dashboard_id" { value = databricks_dashboard.market.id }
output "raw_volume_path" {
  value = "/Volumes/${var.catalog}/${var.schema_prefix}_bronze/raw_files"
}
