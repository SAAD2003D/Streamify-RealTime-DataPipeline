# terraform/outputs.tf

output "data_lake_bucket_name" {
  description = "The name of the created GCS data lake bucket."
  value       = google_storage_bucket.data_lake_bucket.name
}

output "data_lake_bucket_url" {
  description = "The URL of the created GCS data lake bucket."
  value       = google_storage_bucket.data_lake_bucket.url
}

output "bigquery_dataset_id_full" {
  description = "The full ID of the BigQuery dataset (project:dataset)."
  value       = google_bigquery_dataset.analytics_dataset.id # This will be like "project-id:dataset_id"
}