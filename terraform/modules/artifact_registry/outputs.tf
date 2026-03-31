output "repository_id" {
  description = "Artifact Registry repository ID"
  value       = google_artifact_registry_repository.pokemon_tcg.repository_id
}

output "repository_url" {
  description = "Docker registry URL (use as image prefix)"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.pokemon_tcg.repository_id}"
}
