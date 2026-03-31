from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

__all__ = ["router"]

router = APIRouter(tags=["health"])


class _HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=_HealthResponse)
async def health() -> _HealthResponse:
    return _HealthResponse(status="ok", service="public-api")
