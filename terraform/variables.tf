# terraform/variables.tf

variable "gcp_project_id" {
  description = "The GCP project ID where resources will be deployed."
  type        = string
  # No default - must be provided (e.g., via terraform.tfvars or environment variable)
}

variable "gcp_region" {
  description = "The GCP region for resources like GCS buckets and BigQuery datasets."
  type        = string
  default     = "EU" 
}

variable "gcs_bucket_name_data_lake" {
  description = "Name for the GCS bucket (must be globally unique)."
  type        = string
  # No default - must be provided and be globally unique
}

variable "bq_dataset_id" {
  description = "ID for the BigQuery dataset for analytics."
  type        = string
  default     = "streamify_datasets_tf" 
}