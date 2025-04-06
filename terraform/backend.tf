# backend.tf
terraform {
  backend "gcs" {
    bucket = var.gcs_tfstate_bucket_name # References the variable now
    prefix = "terraform/state-free-gcs" 
  }
}