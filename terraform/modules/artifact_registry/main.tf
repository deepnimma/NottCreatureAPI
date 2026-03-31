resource "google_artifact_registry_repository" "pokemon_tcg" {
  project       = var.project_id
  location      = var.region
  repository_id = "pokemon-tcg"
  format        = "DOCKER"
  description   = "Docker images for Pokemon TCG API services"
}
