terraform {
  required_version = ">= 1.9, < 2.0"
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.140.0"
    }
  }
}

provider "databricks" {}
