output "bucket_name" {
  description = "Name of the GCS images bucket"
  value       = google_storage_bucket.images.name
}

output "bucket_url" {
  description = "GCS URL of the images bucket"
  value       = google_storage_bucket.images.url
}
