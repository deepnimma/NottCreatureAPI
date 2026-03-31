from __future__ import annotations

import hashlib
from secrets import token_urlsafe

__all__ = ["generate_api_key", "key_prefix"]


def generate_api_key() -> tuple[str, str]:
    """Return (raw_key, sha256_hash). Format: ptcg_{token_urlsafe(36)}."""
    raw = f"ptcg_{token_urlsafe(36)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def key_prefix(raw_key: str) -> str:
    """Return first 8 chars of the raw key (e.g. 'ptcg_ab1')."""
    return raw_key[:8]
