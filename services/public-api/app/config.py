import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    google_cloud_project: str
    limits_config_path: str
    firestore_emulator_host: str | None
    cors_allowed_origins: list[str]


def load_settings() -> Settings:
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ValueError("GOOGLE_CLOUD_PROJECT env var is required")

    limits_path = os.environ.get("LIMITS_CONFIG_PATH")
    if not limits_path:
        raise ValueError("LIMITS_CONFIG_PATH env var is required")

    origins_raw = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000")
    origins = [o.strip() for o in origins_raw.split(",") if o.strip()]

    return Settings(
        google_cloud_project=project,
        limits_config_path=limits_path,
        firestore_emulator_host=os.environ.get("FIRESTORE_EMULATOR_HOST") or None,
        cors_allowed_origins=origins,
    )


settings = load_settings()
