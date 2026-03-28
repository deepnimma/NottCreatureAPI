---
name: public-api
description: Consumer-facing FastAPI service with tiered rate limiting, Firestore backend, and strict config/logging conventions
---

## Activation

This skill triggers when editing these files:
- `services/public-api/**/*.py`
- `services/public-api/config/*.yaml`

Keywords: public-api, rate limit, slowapi, tier, owner, premium, standard, limits.yaml

---

You are working on the **NottCreatureAPI public-api service** — consumer-facing, tiered rate limiting, Firestore-backed.

## Key Files
- `services/public-api/main.py` — Entry point (scaffolded placeholder, not yet a FastAPI app)
- `services/public-api/app/config.py` — Settings dataclass; `settings = load_settings()` runs at **import time**
- `services/public-api/app/logging.py` — JSON formatter; always use `get_logger(name)` from here
- `services/public-api/config/limits.yaml` — Rate tier definitions (owner/premium/standard)

## Key Concepts
- **Settings are frozen at import:** `config.py` calls `load_settings()` at module level (line 33). Any module that imports `app.config` will crash immediately if `GOOGLE_CLOUD_PROJECT` or `LIMITS_CONFIG_PATH` are unset.
- **Logger idempotency:** `get_logger()` checks `if not logger.handlers` before adding a handler — safe to call multiple times for the same name without duplicating handlers.
- **`trace_id` is optional on log records:** `_JsonFormatter` includes it only if set via `logging.LogRecord` extra. Pass as `extra={"trace_id": ...}` in log calls.
- **CORS origins parsed from env:** `CORS_ALLOWED_ORIGINS` is a comma-separated string defaulting to `http://localhost:3000`.

## Critical Rules
- Never import `app.config` in test setup without setting `GOOGLE_CLOUD_PROJECT` and `LIMITS_CONFIG_PATH` first — it raises `ValueError` at import, not at call time.
- Never call `logging.getLogger()` directly — use `get_logger(name)` from `app.logging` to get the JSON formatter.
- Rate tier changes go in `limits.yaml` only — no hardcoded limits in application code.
- `owner` tier has `rate_limit: null` (unlimited) — don't assume all tiers have numeric limits when parsing the YAML.

## References
- **Patterns:** `.claude/guidelines/public-api/patterns.md`
- **Error Handling:** `.claude/guidelines/error-handling.md`

---
**Last Updated:** 2026-03-28
