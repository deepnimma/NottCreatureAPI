---
name: admin-api
description: Admin API service for managing Pokemon TCG data — GCS image storage, API key auth, Firestore writes
---

## Activation

This skill triggers when editing these files:
- `services/admin-api/**/*`

Keywords: admin-api, admin api, GCS, image upload, ADMIN_API_KEY, GCS_BUCKET

---

You are implementing **admin-api** — an internal FastAPI service (port 8001) for managing Pokemon TCG card data and images.

## Key Files
- `docker-compose.yml` — env vars and service deps (source of truth until config.py exists)
- `services/admin-api/` — service root (currently scaffolded, no source yet)

## Required Environment Variables
- `GOOGLE_CLOUD_PROJECT` — `pokemon-tcg-dev` in dev
- `FIRESTORE_EMULATOR_HOST` — `firestore-emulator:8080` in dev
- `STORAGE_EMULATOR_HOST` — `http://fake-gcs:4443` in dev
- `GCS_BUCKET` — `pokemon-tcg-images`
- `ADMIN_API_KEY` — `dev-secret-key` in dev; all requests must be gated on this

## Key Concepts
- **API Key Auth:** Every endpoint must validate the `ADMIN_API_KEY` header — this is the only auth mechanism. No OAuth, no JWT.
- **GCS image storage:** Images go to the `GCS_BUCKET` bucket via `STORAGE_EMULATOR_HOST` in dev; use the same `fake-gcs` sidecar already defined in docker-compose.
- **Emulators in dev:** Both Firestore and GCS use local emulators — mirror the env var pattern from `public-api`'s `config.py` and `logging.py` when implementing.

## Critical Rules
- Follow the same config-crashes-at-import pattern as `public-api` — call `load_settings()` at module level and raise `ValueError` for missing required vars.
- Use `get_logger(name)` from `app.logging` (copy or share the module from `public-api`) — never raw `logging.getLogger()`.
- Do NOT import from `public-api` directly — each service is independently deployable; share nothing at runtime.
- `mypy strict` + `ruff` apply to this service too (`make lint` covers both).

## References
- **Patterns:** `.claude/guidelines/admin-api/patterns.md`
- **Error Handling:** `.claude/guidelines/error-handling.md`

---
**Last Updated:** 2026-03-28
