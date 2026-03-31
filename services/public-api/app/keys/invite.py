from __future__ import annotations

from typing import Any

from fastapi import HTTPException

__all__ = ["validate_and_consume_invite"]


async def validate_and_consume_invite(db: Any, code: str) -> None:
    """Check invite code is valid and unused, then mark it used.

    Raises HTTPException 404 if code doesn't exist, 409 if already used.
    """
    ref = db.collection("invite_codes").document(code)
    doc = await ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    data: dict[str, Any] = doc.to_dict() or {}
    if data.get("used", False):
        raise HTTPException(status_code=409, detail="Invite code already used")

    await ref.update({"used": True})
