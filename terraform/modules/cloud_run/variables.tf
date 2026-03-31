variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
}

variable "image" {
  description = "Container image URI (e.g. us-central1-docker.pkg.dev/PROJECT/pokemon-tcg/public-api:latest)"
  type        = string
}

variable "service_account_email" {
  description = "Service account email to run the container as"
  type        = string
}

variable "env_vars" {
  description = "Plain environment variables to set on the container"
  type        = map(string)
  default     = {}
}

variable "secret_env_vars" {
  description = "Environment variables sourced from Secret Manager"
  type = list(object({
    name        = string
    secret_name = string
    version     = string
  }))
  default = []
}

variable "min_instances" {
  description = "Minimum number of container instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of container instances"
  type        = number
  default     = 10
}

variable "memory" {
  description = "Memory limit per container instance"
  type        = string
  default     = "256Mi"
}

variable "cpu" {
  description = "CPU limit per container instance"
  type        = string
  default     = "1"
}

variable "allow_public_access" {
  description = "If true, grants allUsers the roles/run.invoker role (public API)"
  type        = bool
  default     = false
}
