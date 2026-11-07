variable "catalog" {
  type    = string
  default = "workspace"
  validation {
    condition     = can(regex("^[a-zA-Z_][a-zA-Z0-9_]*$", var.catalog))
    error_message = "Use a simple catalog identifier."
  }
}

variable "schema_prefix" {
  type    = string
  default = "vn_jobs"
  validation {
    condition     = can(regex("^[a-zA-Z_][a-zA-Z0-9_]*$", var.schema_prefix))
    error_message = "Use a simple schema prefix."
  }
}

variable "warehouse_id" {
  type        = string
  description = "Existing serverless SQL warehouse ID; derived from DATABRICKS_HTTP_PATH."
}

variable "workspace_path" {
  type    = string
  default = "/Shared/vn-it-jobs"
}

variable "enable_liquid_clustering" {
  type    = bool
  default = true
}
