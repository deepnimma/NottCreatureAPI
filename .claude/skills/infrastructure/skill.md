---
name: infrastructure
description: Docker Compose local dev setup with Firestore and GCS emulators for NottCreatureAPI
---

## Activation

This skill triggers when editing these files:
- `docker-compose.yml`
- `terraform/**/*.tf`

Keywords: docker, compose, firestore emulator, fake-gcs, infrastructure, emulator, container

---

You are working on **local dev infrastructure** for NottCreatureAPI.

## Key Files
- `docker-compose.yml` — All four services: `public-api`, `admin-api`, `firestore-emulator`, `fake-gcs`

## Service Map
| Service | Host Port | Notes |
|---|---|---|
| `public-api` | 8000 | no GCS dep |
| `admin-api` | 8001 | needs both emulators |
| `firestore-emulator` | 8080 | `google/cloud-sdk:slim` |
| `fake-gcs` | 4443 | `fsouza/fake-gcs-server`, http scheme |

## Critical Rules
- **`GOOGLE_CLOUD_PROJECT` must be `pokemon-tcg-dev`** in local dev — this value is baked into the Firestore emulator `--project` flag; mismatching it causes auth errors against the emulator.
- **`fake-gcs` runs HTTP not HTTPS** — launched with `-scheme http`. `STORAGE_EMULATOR_HOST` must be `http://fake-gcs:4443` (not `https://`).
- **`fake-gcs-data` volume persists across restarts** — `make down` removes volumes. If you need a clean GCS state, run `make down` (not `docker compose stop`).
- **`public-api` has no GCS env vars** — only admin-api needs `STORAGE_EMULATOR_HOST` and `GCS_BUCKET`. Don't add GCS env to public-api.
- **`develop.watch` syncs to `/app`** — hot-reload works via `docker compose watch` (i.e., `make dev`). `make dev-build` is needed after dependency changes.

## References
- **Patterns:** `.claude/guidelines/infrastructure/patterns.md`
- **Error Handling:** `.claude/guidelines/error-handling.md`

---
**Last Updated:** 2026-03-28
