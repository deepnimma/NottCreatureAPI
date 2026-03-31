from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

__all__ = ["ApiKeyResponse", "KeyRegistrationRequest", "KeyRotationResponse"]


class KeyRegistrationRequest(BaseModel):
    invite_code: str
    label: str | None = None


class ApiKeyResponse(BaseModel):
    prefix: str
    tier: str
    label: str | None
    created_at: datetime
    last_used_at: datetime | None


class KeyRotationResponse(BaseModel):
    key: str
    prefix: str
