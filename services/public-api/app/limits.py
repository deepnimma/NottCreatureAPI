from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

__all__ = ["RateLimit", "get_limit", "load_limits"]

_limits: dict[str, RateLimit] | None = None


@dataclass(frozen=True)
class RateLimit:
    requests_per_minute: int | None
    requests_per_day: int | None


def load_limits(path: str) -> dict[str, RateLimit]:
    global _limits
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    tiers: dict[str, Any] = raw["tiers"]
    _limits = {}
    for tier, cfg in tiers.items():
        rate_cfg: dict[str, Any] | None = (cfg or {}).get("rate_limit")
        if rate_cfg is None:
            _limits[tier] = RateLimit(requests_per_minute=None, requests_per_day=None)
        else:
            _limits[tier] = RateLimit(
                requests_per_minute=rate_cfg.get("requests_per_minute"),
                requests_per_day=rate_cfg.get("requests_per_day"),
            )
    return _limits


def get_limit(tier: str) -> RateLimit:
    if _limits is None:
        raise RuntimeError("Limits not loaded — call load_limits() at startup")
    return _limits[tier]
