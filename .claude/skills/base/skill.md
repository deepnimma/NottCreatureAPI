---
name: base
description: Core conventions, tech stack, and project structure for NottCreatureAPI
---

## Activation

This is a **base skill** that always loads when working in this repository.

---

You are working in **NottCreatureAPI** — a Pokemon TCG data API (early-stage monorepo).

## Tech Stack
FastAPI | Python 3.12 | Pydantic v2 | Google Firestore | GCS | slowapi | Docker Compose | Terraform

## Services
- `public-api` (port 8000) — consumer-facing, tiered rate limiting (owner/premium/standard) via slowapi
- `admin-api` (port 8001) — internal, API key auth, GCS image storage (scaffolded, not yet implemented)

## Commands
- `make dev` — Start with hot-reload (`docker compose watch`)
- `make dev-build` — Rebuild and start
- `make down` — Tear down (removes volumes)
- `make test` — `uv run pytest tests/ -v` per service
- `make lint` — ruff check + mypy strict
- `make format` — ruff format + ruff check --fix
- `make tf-plan-dev` / `make tf-apply-dev` — Terraform dev env

## Critical Conventions
- **Config crashes at import time** — `app/config.py` calls `load_settings()` at module level. `GOOGLE_CLOUD_PROJECT` and `LIMITS_CONFIG_PATH` must be set before importing it; missing = hard `ValueError` at startup.
- **Always use `get_logger(name)`** from `app.logging` — never `logging.getLogger()` directly. Raw calls bypass the JSON formatter.
- **mypy strict + no_implicit_reexport** — all code must be fully typed; re-exports require explicit `__all__`.
- **Rate limits live in YAML** — `services/public-api/config/limits.yaml` (owner=unlimited, premium=120rpm/20k rpd, standard=30rpm/3k rpd). `LIMITS_CONFIG_PATH` env var points to this file.
- **Local dev uses emulators** — Firestore emulator on `:8080`, fake-gcs on `:4443`. Set `FIRESTORE_EMULATOR_HOST=firestore-emulator:8080` and `STORAGE_EMULATOR_HOST=http://fake-gcs:4443` in dev.

## Structure
- `services/public-api/` — Consumer API (FastAPI, implemented)
- `services/public-api/app/` — `config.py`, `logging.py` (core modules)
- `services/public-api/config/limits.yaml` — Rate limit tier definitions
- `services/admin-api/` — Admin API (scaffolded only)
- `terraform/` — Infrastructure as code (`environments/dev/`, `bootstrap/`)

---
**Last Updated:** 2026-03-28
