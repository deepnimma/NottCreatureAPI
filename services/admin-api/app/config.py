from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = ["Settings", "settings"]


@dataclass(frozen=True)
class Settings:
    google_cloud_project: str
    admin_api_key: str
    gcs_bucket: str
    firestore_emulator_host: str | None
    storage_emulator_host: str | None


def load_settings() -> Settings:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ValueError("GOOGLE_CLOUD_PROJECT env var is required")

    admin_api_key = os.environ.get("ADMIN_API_KEY")
    if not admin_api_key:
        raise ValueError("ADMIN_API_KEY env var is required")

    gcs_bucket = os.environ.get("GCS_BUCKET")
    if not gcs_bucket:
        raise ValueError("GCS_BUCKET env var is required")

    return Settings(
        google_cloud_project=project,
        admin_api_key=admin_api_key,
        gcs_bucket=gcs_bucket,
        firestore_emulator_host=os.environ.get("FIRESTORE_EMULATOR_HOST") or None,
        storage_emulator_host=os.environ.get("STORAGE_EMULATOR_HOST") or None,
    )


settings = load_settings()
