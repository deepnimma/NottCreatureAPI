terraform {
  required_version = "~> 1.7"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Copy backend.tf.example → backend.tf and fill in your bucket name before running terraform init
  # backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}
