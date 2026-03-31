from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, Request

from app.db.firestore import get_firestore
from app.logging import get_logger
from app.rate_limit import set_request_tier

__all__ = ["AuthedKey", "require_api_key"]

logger = get_logger(__name__)


@dataclass(frozen=True)
class AuthedKey:
    key_id: str
    prefix: str
    tier: str


async def _update_last_used(db: Any, key_id: str) -> None:
    try:
        await db.collection("api_keys").document(key_id).update(
            {"last_used_at": datetime.now(UTC)}
        )
    except Exception:
        logger.warning("Failed to update last_used_at for key %s", key_id)


async def require_api_key(
    request: Request,
    db: Annotated[Any, Depends(get_firestore)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> AuthedKey:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    doc = await db.collection("api_keys").document(key_hash).get()

    if not doc.exists:
        raise HTTPException(status_code=401, detail="Invalid API key")

    data: dict[str, Any] = doc.to_dict() or {}
    if not data.get("active", False):
        raise HTTPException(status_code=403, detail="API key is inactive")

    authed = AuthedKey(
        key_id=doc.id,
        prefix=str(data.get("prefix", "")),
        tier=str(data.get("tier", "standard")),
    )
    request.state.authed_key = authed
    set_request_tier(authed.tier)
    asyncio.create_task(_update_last_used(db, doc.id))
    return authed
