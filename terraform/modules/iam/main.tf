resource "google_service_account" "public_api" {
  project      = var.project_id
  account_id   = "public-api-sa"
  display_name = "Public API Service Account"
}

resource "google_service_account" "admin_api" {
  project      = var.project_id
  account_id   = "admin-api-sa"
  display_name = "Admin API Service Account"
}

resource "google_service_account" "cicd" {
  project      = var.project_id
  account_id   = "cicd-sa"
  display_name = "CI/CD Service Account"
}

# ── public-api-sa roles ───────────────────────────────────────────────────────

resource "google_project_iam_member" "public_api_datastore_viewer" {
  project = var.project_id
  role    = "roles/datastore.viewer"
  member  = "serviceAccount:${google_service_account.public_api.email}"
}

resource "google_project_iam_member" "public_api_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.public_api.email}"
}

# ── admin-api-sa roles ────────────────────────────────────────────────────────

resource "google_project_iam_member" "admin_api_datastore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.admin_api.email}"
}

resource "google_project_iam_member" "admin_api_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.admin_api.email}"
}

resource "google_project_iam_member" "admin_api_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.admin_api.email}"
}

# ── cicd-sa roles ─────────────────────────────────────────────────────────────

resource "google_project_iam_member" "cicd_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}
