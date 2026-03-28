---
name: rate-limiting
description: Tier-based API quota system using slowapi — config, tier rules, and wiring conventions
---

## Activation

This skill triggers when editing these files:
- `services/public-api/config/limits.yaml`
- `services/public-api/app/middleware/**`
- `services/public-api/app/dependencies/**`

Keywords: rate limit, slowapi, tier, quota, rpm, rpd, owner, premium, standard

---

You are working on **rate limiting** in NottCreatureAPI's `public-api` service.

## Key Files
- `services/public-api/config/limits.yaml` — Single source of truth for all tier quotas
- `services/public-api/app/config.py` — `LIMITS_CONFIG_PATH` env var points to the yaml at runtime

## Tier Definitions
| Tier | RPM | RPD |
|------|-----|-----|
| `owner` | unlimited (`null`) | unlimited |
| `premium` | 120 | 20,000 |
| `standard` | 30 | 3,000 |

## Key Concepts
- **`rate_limit: null`** means unlimited — do not replace with a large number; null is the sentinel for "bypass limiting" in the owner tier.
- **`LIMITS_CONFIG_PATH`** must be set before importing `app.config` — config crashes at import if missing (see base skill).
- **slowapi ≥0.1.9** is the declared dependency — not yet wired; integration should attach a `Limiter` to the FastAPI app in `main.py` and inject it via dependency or middleware.

## Critical Rules
- Never hardcode tier limits in Python — all quota values must come from `limits.yaml` loaded via `Settings`.
- Both RPM and RPD limits must be enforced per tier; applying only one leaves the other unbounded.
- `owner` tier bypass must check for `null` explicitly — do not fall through to a default limit.

## References
- **Patterns:** `.claude/guidelines/rate-limiting/patterns.md`
- **Error Handling:** `.claude/guidelines/error-handling.md`

---
**Last Updated:** 2026-03-28
