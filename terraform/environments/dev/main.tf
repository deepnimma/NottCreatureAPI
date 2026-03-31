module "iam" {
  source     = "../../modules/iam"
  project_id = var.project_id
}

module "firestore" {
  source     = "../../modules/firestore"
  project_id = var.project_id
  region     = var.region
}

module "storage" {
  source      = "../../modules/storage"
  project_id  = var.project_id
  region      = var.region
  bucket_name = var.images_bucket_name
}

module "artifact_registry" {
  source     = "../../modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
}

module "public_api" {
  source = "../../modules/cloud_run"

  project_id            = var.project_id
  region                = var.region
  service_name          = "public-api"
  image                 = var.image_public_api
  service_account_email = module.iam.public_api_sa_email
  allow_public_access   = true

  env_vars = {
    GOOGLE_CLOUD_PROJECT = var.project_id
    LIMITS_CONFIG_PATH   = "/app/config/limits.yaml"
  }
}

module "admin_api" {
  source = "../../modules/cloud_run"

  project_id            = var.project_id
  region                = var.region
  service_name          = "admin-api"
  image                 = var.image_admin_api
  service_account_email = module.iam.admin_api_sa_email
  allow_public_access   = false

  env_vars = {
    GOOGLE_CLOUD_PROJECT = var.project_id
    GCS_BUCKET           = module.storage.bucket_name
  }

  secret_env_vars = [
    {
      name        = "ADMIN_API_KEY"
      secret_name = var.admin_api_key_secret_name
      version     = "latest"
    }
  ]
}

# ── Outputs ───────────────────────────────────────────────────────────────────

output "public_api_url" {
  value = module.public_api.service_url
}

output "admin_api_url" {
  value = module.admin_api.service_url
}

output "images_bucket_name" {
  value = module.storage.bucket_name
}

output "artifact_registry_url" {
  value = module.artifact_registry.repository_url
}
