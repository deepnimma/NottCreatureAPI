output "public_api_sa_email" {
  description = "Email of the public-api service account"
  value       = google_service_account.public_api.email
}

output "admin_api_sa_email" {
  description = "Email of the admin-api service account"
  value       = google_service_account.admin_api.email
}

output "cicd_sa_email" {
  description = "Email of the CI/CD service account"
  value       = google_service_account.cicd.email
}
