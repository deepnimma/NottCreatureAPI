from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request

from app.auth import AuthedKey, require_api_key
from app.db.firestore import get_firestore
from app.keys.generator import generate_api_key, key_prefix
from app.keys.invite import validate_and_consume_invite
from app.models.key import ApiKeyResponse, KeyRegistrationRequest, KeyRotationResponse
from app.rate_limit import limiter, rpm_limit

__all__ = ["router"]

router = APIRouter(tags=["keys"])


@router.post("/keys", response_model=KeyRotationResponse, status_code=201)
async def register_key(
    body: KeyRegistrationRequest,
    db: Annotated[Any, Depends(get_firestore)],
) -> KeyRotationResponse:
    await validate_and_consume_invite(db, body.invite_code)

    raw_key, key_hash = generate_api_key()
    prefix = key_prefix(raw_key)

    await db.collection("api_keys").document(key_hash).set(
        {
            "prefix": prefix,
            "tier": "standard",
            "active": True,
            "label": body.label,
            "created_at": datetime.now(UTC),
            "last_used_at": None,
        }
    )

    return KeyRotationResponse(key=raw_key, prefix=prefix)


@router.get("/keys/me", response_model=ApiKeyResponse)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def get_my_key(
    request: Request,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
) -> ApiKeyResponse:
    doc = await db.collection("api_keys").document(authed_key.key_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Key not found")

    data: dict[str, Any] = doc.to_dict() or {}
    return ApiKeyResponse(
        prefix=str(data.get("prefix", "")),
        tier=str(data.get("tier", "standard")),
        label=data.get("label"),
        created_at=data["created_at"],
        last_used_at=data.get("last_used_at"),
    )


@router.post("/keys/rotate", response_model=KeyRotationResponse)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def rotate_key(
    request: Request,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
) -> KeyRotationResponse:
    old_doc = await db.collection("api_keys").document(authed_key.key_id).get()
    if not old_doc.exists:
        raise HTTPException(status_code=404, detail="Key not found")

    old_data: dict[str, Any] = old_doc.to_dict() or {}

    raw_key, key_hash = generate_api_key()
    prefix = key_prefix(raw_key)

    await db.collection("api_keys").document(key_hash).set(
        {
            "prefix": prefix,
            "tier": old_data.get("tier", "standard"),
            "active": True,
            "label": old_data.get("label"),
            "created_at": datetime.now(UTC),
            "last_used_at": None,
        }
    )
    await db.collection("api_keys").document(authed_key.key_id).update({"active": False})

    return KeyRotationResponse(key=raw_key, prefix=prefix)


@router.delete("/keys/me", status_code=204)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def revoke_key(
    request: Request,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
) -> None:
    await db.collection("api_keys").document(authed_key.key_id).update({"active": False})
