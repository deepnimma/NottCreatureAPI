variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "images_bucket_name" {
  description = "GCS bucket name for card images (must be globally unique)"
  type        = string
}

variable "image_public_api" {
  description = "Container image URI for public-api"
  type        = string
}

variable "image_admin_api" {
  description = "Container image URI for admin-api"
  type        = string
}

variable "admin_api_key_secret_name" {
  description = "Secret Manager secret name for ADMIN_API_KEY (must exist before apply)"
  type        = string
  default     = "pokemon-tcg-admin-api-key"
}
