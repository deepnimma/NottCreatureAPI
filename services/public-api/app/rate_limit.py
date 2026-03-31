from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.limits import get_limit

if TYPE_CHECKING:
    from app.auth import AuthedKey

__all__ = ["limiter", "rpm_limit", "rpd_limit", "set_request_tier"]

# Per-request tier, set by require_api_key before rate limit check runs
_request_tier: ContextVar[str] = ContextVar("_request_tier", default="standard")


def set_request_tier(tier: str) -> None:
    _request_tier.set(tier)


def _key_from_prefix(request: Request) -> str:
    authed: AuthedKey | None = getattr(request.state, "authed_key", None)
    if authed is not None:
        return authed.prefix
    ip: str = get_remote_address(request)
    return ip


limiter: Any = Limiter(key_func=_key_from_prefix)


def rpm_limit() -> str:
    tier = _request_tier.get()
    limit = get_limit(tier)
    rpm = limit.requests_per_minute
    return f"{rpm}/minute" if rpm is not None else "9999999/minute"


def rpd_limit() -> str:
    tier = _request_tier.get()
    limit = get_limit(tier)
    rpd = limit.requests_per_day
    return f"{rpd}/day" if rpd is not None else "9999999/day"
