# variables.tf
variable "gcp_project_id" {
  description = "The GCP Project ID (MUST BE PROVIDED via terraform.tfvars or -var)"
  type        = string
}

variable "gcp_region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1" # Change if needed
}

variable "gcs_tfstate_bucket_name" {
  description = "Globally unique GCS bucket name for Terraform state (MUST BE PROVIDED via terraform.tfvars or -var)"
  type        = string
}

variable "gcs_staging_bucket_name_suffix" {
   description = "Suffix for the GCS staging bucket name (prefix is project_id)"
   type        = string
   default     = "streamify-staging-free"
}

variable "pubsub_topic_name" {
  description = "Name for the Pub/Sub topic"
  type        = string
  default     = "streamify-events-free" 
}

variable "pubsub_gcs_subscription_name" {
  description = "Name for the Pub/Sub subscription feeding GCS"
  type        = string
  default     = "streamify-events-free-to-gcs" 
}

variable "bq_dataset_name" {
  description = "Name for the BigQuery dataset"
  type        = string
  default     = "streamify_data_free"
}

variable "bq_raw_table_name" {
  description = "Name for the raw BigQuery table receiving GCS data"
  type        = string
  default     = "raw_events_gcs" 
}

variable "load_function_name" {
   description = "Name for the GCS-to-BQ Cloud Function"
   type        = string
   default     = "gcs-to-bq-load-fn"
}

variable "artifacts_bucket_name_suffix" {
    description = "Suffix for the GCS artifacts bucket name (prefix is project_id)"
    type        = string
    default     = "streamify-fn-artifacts"
}

variable "scheduler_job_name" {
    description = "Name for the Cloud Scheduler job placeholder"
    type        = string
    default     = "dbt-run-hourly"
}

variable "scheduler_placeholder_topic_name" {
    description = "Name for the temporary PubSub topic used by Scheduler placeholder"
    type        = string
    default     = "scheduler-placeholder-free"
}