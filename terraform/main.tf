resource "google_storage_bucket" "data_lake_bucket" {
  name                        = var.gcs_bucket_name_data_lake
  location                    = var.gcp_region
  uniform_bucket_level_access = true
  storage_class               = "STANDARD" # Or REGIONAL, NEARLINE, COLDLINE as needed

 

  labels = {
    environment = "dev" # Or your environment (dev, staging, prod)
    purpose     = "streamify-data-lake"
    managed_by  = "terraform"
  }
}

# --- BigQuery Dataset ---
resource "google_bigquery_dataset" "analytics_dataset" {
  dataset_id  = var.bq_dataset_id
  project     = var.gcp_project_id
  location    = var.gcp_region # Often good to keep dataset in same region as GCS bucket
  description = "Dataset for Streamify analytics, managed by Terraform. Tables created by Airflow."

  labels = {
    environment = "dev"
    purpose     = "streamify-analytics"
    managed_by  = "terraform"
  }
}