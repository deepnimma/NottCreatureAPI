output "state_bucket_name" {
  description = "Name of the GCS bucket used for Terraform state"
  value       = google_storage_bucket.tf_state.name
}
