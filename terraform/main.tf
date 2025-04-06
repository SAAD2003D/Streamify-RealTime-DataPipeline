# main.tf

# --- Get Project Number (used for service agent emails) ---
data "google_project" "project" {
  project_id = var.gcp_project_id
}

# --- Pub/Sub Topic ---
resource "google_pubsub_topic" "event_topic" {
  name    = var.pubsub_topic_name
  project = var.gcp_project_id
}

# --- GCS Bucket for Staging Pub/Sub Messages ---
resource "google_storage_bucket" "staging_bucket" {
  name          = "${var.gcp_project_id}-${var.gcs_staging_bucket_name_suffix}" 
  location      = var.gcp_region
  force_destroy = false 
  project       = var.gcp_project_id
  storage_class = "STANDARD" 
  uniform_bucket_level_access = true
}

# --- IAM: Allow Pub/Sub to Write to Staging Bucket ---
resource "google_project_iam_member" "pubsub_gcs_binding" {
  project = var.gcp_project_id
  role    = "roles/storage.objectCreator"
  member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

# --- Pub/Sub Subscription to GCS ---
resource "google_pubsub_subscription" "gcs_subscription" {
  name    = var.pubsub_gcs_subscription_name
  topic   = google_pubsub_topic.event_topic.name
  project = var.gcp_project_id
  ack_deadline_seconds = 60 

  cloud_storage_config {
    bucket = google_storage_bucket.staging_bucket.name
    filename_prefix       = "events/" 
    filename_suffix       = ".json"   
    max_duration          = "300s"    
    max_bytes             = 10485760  
    json_config { write_metadata = true }
  }
  depends_on = [google_project_iam_member.pubsub_gcs_binding]
}

# --- BigQuery Dataset ---
resource "google_bigquery_dataset" "streamify_dataset" {
  dataset_id    = var.bq_dataset_name
  friendly_name = "Streamify Pipeline Data (Free Tier + GCS)"
  location      = var.gcp_region
  project       = var.gcp_project_id
}

# --- BigQuery Raw Staging Table ---
resource "google_bigquery_table" "raw_events_table" {
  dataset_id = google_bigquery_dataset.streamify_dataset.dataset_id
  table_id   = var.bq_raw_table_name
  project    = var.gcp_project_id
  # Schema reflects structure including Pub/Sub metadata + data payload as string
  schema = jsonencode([
    {"name": "subscription_name", "type": "STRING", "mode": "NULLABLE"},
    {"name": "message_id",        "type": "STRING", "mode": "NULLABLE"},
    {"name": "publish_time",      "type": "TIMESTAMP", "mode": "NULLABLE"},
    {"name": "data",              "type": "STRING", "mode": "NULLABLE"}, # Storing raw JSON payload as string
    {"name": "attributes",        "type": "STRING", "mode": "NULLABLE"}, # Storing attributes JSON as string
    {"name": "gcs_source_file",   "type": "STRING", "mode": "NULLABLE"}, # To be added by function
    {"name": "load_timestamp",    "type": "TIMESTAMP","mode": "NULLABLE"}  # To be added by function
  ])
}

# --- GCS Bucket for Cloud Function Source Code / Artifacts ---
 resource "google_storage_bucket" "artifacts_bucket" {
  name                        = "${var.gcp_project_id}-${var.artifacts_bucket_name_suffix}" 
  location                    = var.gcp_region
  project                     = var.gcp_project_id
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = false 
}

# --- Service Account for GCS -> BQ Load Function ---
resource "google_service_account" "gcs_to_bq_loader_sa" {
  account_id   = "gcs-bq-load-fn-sa"
  display_name = "SA for GCS to BQ Loader Function"
  project      = var.gcp_project_id
}

# --- IAM for GCS -> BQ Load Function ---
# Allow Function to Read Staging Bucket
resource "google_storage_bucket_iam_member" "gcs_read_binding" {
  bucket = google_storage_bucket.staging_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.gcs_to_bq_loader_sa.email}"
}
# Allow Function to Write BQ Data & Metadata & Run Jobs
resource "google_project_iam_member" "bq_write_binding" {
  project = var.gcp_project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.gcs_to_bq_loader_sa.email}"
}
resource "google_project_iam_member" "bq_metadata_binding" {
   project = var.gcp_project_id
   role    = "roles/bigquery.metadataViewer"
   member  = "serviceAccount:${google_service_account.gcs_to_bq_loader_sa.email}"
}
 resource "google_project_iam_member" "bq_jobuser_binding" {
   project = var.gcp_project_id
   role    = "roles/bigquery.jobUser"
   member  = "serviceAccount:${google_service_account.gcs_to_bq_loader_sa.email}"
}
# Allow Eventarc to trigger the Function
resource "google_project_iam_member" "eventarc_trigger_binding" {
  project = var.gcp_project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.gcs_to_bq_loader_sa.email}"
}
# Allow Pub/Sub Service Agent (used by Eventarc for GCS) to create tokens for Function SA
 resource "google_project_iam_member" "eventarc_gcs_binding" {
   project = var.gcp_project_id
   role    = "roles/iam.serviceAccountTokenCreator"
   member  = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
 }
 # Allow Function SA to act as the Eventarc Trigger Service Account
 resource "google_service_account_iam_member" "eventarc_trigger_sa_binding" {
   service_account_id = google_service_account.gcs_to_bq_loader_sa.name
   role               = "roles/iam.serviceAccountUser"
   member             = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
 }

# --- Cloud Function (Gen 2) - Resource Definition ONLY ---
# Deploy the actual code separately after Terraform runs (see Phase 5)
resource "google_cloudfunctions2_function" "gcs_to_bq_loader" {
  name        = var.load_function_name
  location    = var.gcp_region
  project     = var.gcp_project_id

  build_config {
    runtime     = "python39" # Choose your runtime
    entry_point = "load_gcs_to_bq"  # Python function name in your main.py
    source {
       storage_source { # Define source location in GCS
         bucket = google_storage_bucket.artifacts_bucket.name 
         object = "function_source/gcs_to_bq_source.zip" # Path where you will upload the zip
       }
    }
  }
  service_config {
    max_instance_count    = 1 
    min_instance_count    = 0
    available_memory      = "256Mi" # Smallest available
    timeout_seconds       = 300     
    service_account_email = google_service_account.gcs_to_bq_loader_sa.email
    
    # Eventarc Trigger (GCS Object Finalization)
    event_trigger {
      trigger_region = var.gcp_region 
      event_type     = "google.cloud.storage.object.v1.finalized"
      retry_policy   = "RETRY_POLICY_RETRY"
      service_account_email = google_service_account.gcs_to_bq_loader_sa.email # SA the trigger runs as
      event_filters {
         attribute = "bucket"
         value     = google_storage_bucket.staging_bucket.name
      }
    }
  }
  # Ensure IAM roles are set before function creation attempts
  depends_on = [
     google_storage_bucket_iam_member.gcs_read_binding,
     google_project_iam_member.bq_write_binding,
     google_project_iam_member.bq_metadata_binding,
     google_project_iam_member.bq_jobuser_binding,
     google_project_iam_member.eventarc_trigger_binding,
     google_project_iam_member.eventarc_gcs_binding,
     google_service_account_iam_member.eventarc_trigger_sa_binding
  ]
}

# --- Cloud Scheduler Job (Placeholder target) ---
resource "google_cloud_scheduler_job" "dbt_run_scheduler" {
  name        = var.scheduler_job_name
  description = "Triggers the dbt transformation job hourly"
  schedule    = "0 * * * *" # Cron: At minute 0 past every hour
  time_zone   = "Etc/UTC"
  project     = var.gcp_project_id
  region      = var.gcp_region 
   pubsub_target {
     topic_name = google_pubsub_topic.scheduler_placeholder_topic.id 
     data       = base64encode("Trigger dbt run Placeholder")
   }
   attempt_deadline = "320s"
}

# Placeholder Topic for Scheduler
resource "google_pubsub_topic" "scheduler_placeholder_topic" {
  name    = var.scheduler_placeholder_topic_name
  project = var.gcp_project_id
  # Ensure this depends on the scheduler job that targets it
  depends_on = [google_cloud_scheduler_job.dbt_run_scheduler]
}