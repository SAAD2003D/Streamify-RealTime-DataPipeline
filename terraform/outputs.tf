# outputs.tf
output "gcs_staging_bucket_name" {
  description = "Name of the GCS bucket staging Pub/Sub data"
  value       = google_storage_bucket.staging_bucket.name
}
output "gcs_artifacts_bucket_name" {
    description = "Name of the GCS bucket for Function source/artifacts"
    value = google_storage_bucket.artifacts_bucket.name
}
output "pubsub_topic_id" {
  description = "ID of the Pub/Sub topic for events"
  value       = google_pubsub_topic.event_topic.id
}
output "pubsub_gcs_subscription_id" {
  description = "ID of the Pub/Sub subscription feeding GCS"
  value       = google_pubsub_subscription.gcs_subscription.id
}
output "bq_dataset_id" {
  description = "ID of the BigQuery dataset"
  value       = google_bigquery_dataset.streamify_dataset.dataset_id
}
output "bq_raw_table_id" {
  description = "ID of the raw BigQuery table (PROJECT:DATASET.TABLE)"
  value       = google_bigquery_table.raw_events_table.id
}
 output "gcs_to_bq_function_name" {
   description = "Name of the GCS-to-BQ Cloud Function (needs code deployment)"
   value       = google_cloudfunctions2_function.gcs_to_bq_loader.name
 }
output "scheduler_job_name" {
  description = "Name of the Cloud Scheduler job (needs target update)"
  value       = google_cloud_scheduler_job.dbt_run_scheduler.name
}
 output "scheduler_placeholder_topic_id" {
   description = "ID of the temporary PubSub topic used by scheduler placeholder"
   value = google_pubsub_topic.scheduler_placeholder_topic.id
 }