# provider.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" 
    }
  }
  required_version = ">= 1.3" 
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  # zone    = var.gcp_zone
}