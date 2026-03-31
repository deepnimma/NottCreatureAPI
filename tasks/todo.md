# Pokemon TCG API — Implementation Plan

## Stack
- **Language:** Python + FastAPI (backend) | Vue 3 + Vite + TypeScript (admin UI, stretch goal)
- **Package manager:** `uv` (Python), `npm` (UI)
- **Linting/formatting:** `ruff` + `mypy`
- **Database:** Firestore (Native mode, serverless, `us-central1`)
- **Images:** Cloud Storage (public GCS URLs, WebP)
- **Services:** Cloud Run (scale to zero, `us-central1`)
- **IaC:** Terraform | **CI/CD:** GitHub Actions | **DNS:** Cloudflare

## Services
- `services/public-api/` — card/set queries + API key self-service (key required, tier rate-limited)
- `services/admin-api/` — ingestion, invite codes, key management (single owner admin key)
- `services/admin-ui/` — owner-only Vue admin UI (Phase W, stretch goal)
- `scripts/scraper/` — TCGDex data pipeline (Phase S, independent)

---

## How to Read This File

- **Deps:** = must complete first (~~strike~~ when done)
- **Blockers:** = external requirements
- Pick any task whose deps/blockers are all cleared

---

## Phase 0 — Cleanup & Scaffolding ✓

- [x] **0.1** Delete Java/Gradle files
- [x] **0.2** Create directory skeleton
- [x] **0.3** Write root `.gitignore`
- [x] **0.4** Write root `Makefile`
- [x] **0.5** Write `docker-compose.yml`
- [x] **0.6** Write root `pyproject.toml` (ruff + mypy config)

---

## Phase 1 — Terraform Bootstrap & Core Infrastructure

- [x] **1.0** Write `terraform/.terraform-version` (pin `~> 1.7`) and `terraform/versions.tf` (pin Google provider `~> 5.0`)
  - **Deps:** ~~0.2~~

- [x] **1.1** Write `terraform/bootstrap/` (`main.tf` — GCS state bucket, `variables.tf`, `outputs.tf`) — run once manually
  - **Deps:** ~~1.0~~
  - **Blockers:** GCP account with billing; `gcloud auth application-default login`

- [x] **1.2** Write `terraform/modules/iam/` (`main.tf` service accounts + role bindings, `variables.tf`, `outputs.tf`)
  - Accounts: `public-api-sa` (datastore.viewer + storage.objectViewer), `admin-api-sa` (datastore.user + storage.objectAdmin + secretmanager.secretAccessor), `cicd-sa` (artifactregistry.writer + run.admin)
  - **Deps:** ~~0.2~~

- [x] **1.3** Write `terraform/modules/firestore/` (`main.tf` Native mode `us-central1`, `variables.tf`, `outputs.tf`)
  - **Deps:** ~~0.2~~

- [x] **1.4** Write `terraform/modules/storage/` (`main.tf` — public bucket, CORS `*` for dev, lifecycle rule; `variables.tf`, `outputs.tf`)
  - **Deps:** ~~0.2~~

- [x] **1.5** Write `terraform/modules/artifact_registry/` (`main.tf` Docker repo `pokemon-tcg`, `variables.tf`, `outputs.tf`)
  - **Deps:** ~~0.2~~

- [x] **1.6** Write `terraform/modules/cloud_run/` — reusable module; `secret_env_vars` list for Secret Manager refs (`ADMIN_API_KEY`); `allow_public_access` toggle
  - **Deps:** ~~0.2~~

- [x] **1.7** Write `terraform/environments/dev/` (`providers.tf`, `backend.tf.example`, `variables.tf`, `terraform.tfvars.example`, `main.tf` wiring all modules) — `terraform validate` passes
  - **Deps:** ~~1.1~~, ~~1.2~~, ~~1.3~~, ~~1.4~~, ~~1.5~~, ~~1.6~~

- [ ] **1.8** Verify `terraform plan` for dev (0 errors, review resource list)
  - **Deps:** ~~1.7~~
  - **Blockers:** GCP account with billing; bootstrap bucket must exist; real `terraform.tfvars` copied from example

---

## Phase 2 — Public API

- [x] **2.0** `uv init` public-api — add deps (`fastapi`, `uvicorn[standard]`, `google-cloud-firestore`, `pydantic`, `pillow`, `pyyaml`, `slowapi`; dev: `pytest`, `pytest-asyncio`, `httpx`)
  - **Deps:** ~~0.2~~

- [x] **2.0a** Write `services/public-api/.env.example` (documents `GOOGLE_CLOUD_PROJECT`, `FIRESTORE_EMULATOR_HOST`, `LIMITS_CONFIG_PATH`, `CORS_ALLOWED_ORIGINS`)
  - **Deps:** ~~2.0~~

- [x] **2.0b** Write `services/public-api/config/limits.yaml` (initial: owner unlimited, premium 120/min 20k/day, standard 30/min 3k/day)
  - **Deps:** ~~2.0~~

- [x] **2.0c** Write `app/config.py` (frozen `Settings` dataclass from env vars, fails fast on missing required vars)
  - **Deps:** ~~2.0~~

- [x] **2.0d** Write `app/logging.py` (JSON formatter: `timestamp`, `level`, `service`, `message`, `trace_id`; `get_logger(name)` helper)
  - **Deps:** ~~2.0~~

- [x] **2.1** Write Pydantic models (`Attack`, `Ability`, `WeaknessResistance`, `Legality`, `Translation`, `Card`, `CardSummary`, `CardListResponse`, `CardVariant`, `CardVariantResolved`, `CardSet`, `SetListResponse`, `PaginationMeta`, `ErrorResponse`)
  - `CardVariant` has `image_url: str | None`; `CardVariantResolved` adds `effective_image_url: str` (always populated, falls back to parent)
  - **Deps:** ~~2.0~~

- [x] **2.2** Write rate limit config loader (`app/limits.py` — reads `limits.yaml` at startup into frozen dataclass, `get_limit(tier) -> RateLimit`)
  - Note: placed at `app/limits.py` (not `app/config/limits.py`) to avoid Python import conflict with existing `app/config.py`
  - **Deps:** ~~2.0~~

- [x] **2.3** Write API key auth dependency (`app/auth.py` — `X-API-Key` header → SHA-256 → Firestore lookup; 401 missing, 403 inactive; `last_used_at` updated async)
  - **Deps:** ~~2.2~~

- [x] **2.4** Write per-tier rate limiter (`app/rate_limit.py` — `slowapi` keyed by key prefix; owner bypasses; limits from config via ContextVar)
  - **Deps:** ~~2.2~~, ~~2.3~~

- [x] **2.5** Write Firestore read client (`app/db/firestore.py` — emulator-aware; `get_document`, `paginate_collection`)
  - **Deps:** ~~2.1~~

- [x] **2.6** Write `GET /v1/sets` + `GET /v1/sets/{setId}` (auth required, paginated by `release_date`)
  - **Deps:** ~~2.4~~, ~~2.5~~

- [x] **2.7** Write `GET /v1/cards` — basic list, cursor pagination, sort by `number` (no filters yet, auth required)
  - **Deps:** ~~2.4~~, ~~2.5~~

- [x] **2.8** Write `GET /v1/cards/{cardId}` — full card doc; optional `?lang=fr` merges `translations.fr` over base, missing fields fall back to English (auth required)
  - **Deps:** ~~2.4~~, ~~2.5~~

- [x] **2.9** Write `GET /v1/sets/{setId}/cards` (auth required, paginated)
  - **Deps:** ~~2.6~~, ~~2.7~~

- [x] **2.10** Write `GET /v1/health` (no auth, `{"status":"ok","service":"public-api"}`)
  - **Deps:** ~~0.2~~

- [x] **2.11** Write `app/main.py` (FastAPI init, routers, CORS from `config.cors_allowed_origins`, error handlers, slowapi middleware)
  - **Deps:** ~~2.6~~, ~~2.7~~, ~~2.8~~, ~~2.9~~, ~~2.10~~

- [x] **2.12** Write `services/public-api/Dockerfile` (multi-stage `uv sync --frozen`, non-root, uvicorn port 8000)
  - **Deps:** ~~2.11~~

- [x] **2.13** Write pytest suite (list, get, pagination, 404, 401, 403, `?lang=` translation merge — 14 tests, all passing)
  - **Deps:** ~~2.11~~

- [x] **2.14** Verify public API runs locally via docker-compose
  - **Deps:** ~~0.5~~, ~~2.12~~, ~~2.13~~
  - Fixed: `.dockerignore` missing (host `.venv` overwrote builder's); Firestore emulator image changed to `gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators` (Java 21 required)

---

## Phase 2.5 — API Key Management

> Endpoints in `public-api` under `/v1/keys`.

- [x] **2.5.1** Write `app/models/key.py` (`ApiKeyResponse`, `KeyRegistrationRequest`, `KeyRotationResponse`)
  - **Deps:** ~~2.0~~

- [x] **2.5.2** Write invite code validator (`app/keys/invite.py` — check + mark used)
  - **Deps:** ~~2.5~~

- [x] **2.5.3** Write key generator (`app/keys/generator.py` — `ptcg_{token_urlsafe(36)}`, returns `(raw_key, sha256_hash)`)
  - **Deps:** ~~2.5.1~~

- [x] **2.5.4** Write `POST /v1/keys` — invite code → standard tier key, shown **once only**
  - **Deps:** ~~2.5.2~~, ~~2.5.3~~

- [x] **2.5.5** Write `GET /v1/keys/me` — returns prefix/tier/label/dates, no hash (auth required)
  - **Deps:** ~~2.3~~, ~~2.5.1~~

- [x] **2.5.6** Write `POST /v1/keys/rotate` — new key shown once, old deactivated
  - **Deps:** ~~2.5.3~~, ~~2.5.5~~

- [x] **2.5.7** Write `DELETE /v1/keys/me` — self-revoke (`active = false`)
  - **Deps:** ~~2.3~~

- [x] **2.5.8** Write pytest suite (registration, invalid/used code, rotation, self-revoke — 9 tests, all passing)
  - **Deps:** ~~2.5.4~~, ~~2.5.5~~, ~~2.5.6~~, ~~2.5.7~~

---

## Phase 3 — Admin API

- [ ] **3.0** `uv init` admin-api — add deps (`fastapi`, `uvicorn[standard]`, `google-cloud-firestore`, `google-cloud-storage`, `pydantic`, `pillow`, `python-multipart`; dev: `pytest`, `pytest-asyncio`, `httpx`)
  - **Deps:** ~~0.2~~

- [ ] **3.0a** Write `services/admin-api/.env.example` (`GOOGLE_CLOUD_PROJECT`, `ADMIN_API_KEY`, `GCS_BUCKET`, `FIRESTORE_EMULATOR_HOST`, `STORAGE_EMULATOR_HOST`)
  - **Deps:** ~~3.0~~

- [ ] **3.0b** Write `app/config.py` (frozen `Settings`, fails fast on missing vars)
  - **Deps:** ~~3.0~~

- [ ] **3.0c** Write `app/logging.py` (same JSON logging as public-api)
  - **Deps:** ~~3.0~~

- [ ] **3.1** Write admin auth middleware (`X-Admin-Key` header vs `ADMIN_API_KEY` env → 401)
  - **Deps:** ~~3.0~~

- [ ] **3.2** Write GCS client (`upload_image`, `delete_image`, WebP conversion via Pillow; emulator-aware)
  - **Deps:** ~~3.0~~

- [ ] **3.3** Write Firestore write client (`create_document`, `update_document`, `delete_document`, auto-timestamps)
  - **Deps:** ~~3.0~~

- [ ] **3.4** Write `POST /v1/admin/sets` (multipart: metadata + logo + symbol → GCS → Firestore)
  - **Deps:** ~~3.1~~, ~~3.2~~, ~~3.3~~

- [ ] **3.5** Write `PUT /v1/admin/sets/{setId}` (partial metadata update)
  - **Deps:** ~~3.3~~, ~~3.4~~

- [ ] **3.6** Write `POST /v1/admin/cards` (multipart: JSON + base image → `base.webp` + `200px thumb.webp` → Firestore; `image_url` mandatory)
  - **Deps:** ~~3.1~~, ~~3.2~~, ~~3.3~~

- [ ] **3.7** Write `PUT /v1/admin/cards/{cardId}` (partial metadata update, no image fields)
  - **Deps:** ~~3.3~~, ~~3.6~~

- [ ] **3.8** Write `DELETE /v1/admin/cards/{cardId}` (Firestore doc + all GCS images: base, thumb, all variants)
  - **Deps:** ~~3.2~~, ~~3.3~~, ~~3.6~~

- [ ] **3.9** Write admin invite code endpoints (`POST`, `GET`, `DELETE /v1/admin/invite-codes`)
  - **Deps:** ~~3.1~~, ~~3.3~~

- [ ] **3.10** Write admin key management endpoints (`GET /v1/admin/keys`, `PUT /v1/admin/keys/{id}`, `DELETE /v1/admin/keys/{id}`)
  - **Deps:** ~~3.1~~, ~~3.3~~

- [ ] **3.11** Write `PUT /v1/admin/cards/{cardId}/image` (replace image: delete old GCS files, upload new `base.webp` + regenerate `thumb.webp`, update Firestore URLs)
  - **Deps:** ~~3.2~~, ~~3.3~~, ~~3.6~~

- [ ] **3.12** Write `PATCH /v1/admin/cards/{cardId}/translations` (merge `{"lang":"fr", "name":"...", ...}` into `translations.fr` map field; omitted fields untouched)
  - **Deps:** ~~3.3~~, ~~3.6~~

- [ ] **3.13** Write `app/main.py`
  - **Deps:** ~~3.4~~, ~~3.5~~, ~~3.6~~, ~~3.7~~, ~~3.8~~, ~~3.9~~, ~~3.10~~, ~~3.11~~, ~~3.12~~

- [ ] **3.14** Write `services/admin-api/Dockerfile` (multi-stage uv, non-root, uvicorn port 8000)
  - **Deps:** ~~3.13~~

- [ ] **3.15** Write pytest suite (card/set CRUD, image replace, translation patch, invite codes, key management, 401 on all routes)
  - **Deps:** ~~3.13~~

- [ ] **3.16** Verify admin API runs locally via docker-compose
  - **Deps:** ~~0.5~~, ~~3.14~~, ~~3.15~~

---

## Phase 4 — GitHub Actions CI/CD

- [ ] **4.1** Write Workload Identity Federation Terraform config (WIF Pool + Provider bound to `cicd-sa`)
  - **Deps:** ~~1.2~~

- [ ] **4.2** Write `.github/workflows/ci.yml` (PR: ruff + mypy + pytest matrix for both services; uv installs; emulators as service containers)
  - **Deps:** ~~2.13~~, ~~3.15~~

- [ ] **4.3** Write `.github/workflows/deploy.yml` (main push: WIF auth → build + push to Artifact Registry → `terraform apply` → Cloud Run deploy both services)
  - **Deps:** ~~4.1~~, ~~2.12~~, ~~3.14~~

- [ ] **4.4** Configure GitHub secrets (`GCP_PROJECT_ID`, `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`)
  - **Deps:** ~~4.1~~
  - **Blockers:** GitHub repo created; Terraform dev apply run (WIF resources exist)

- [ ] **4.5** Verify CI passes on a test PR
  - **Deps:** ~~4.2~~, ~~4.4~~

- [ ] **4.6** Verify deploy pipeline end-to-end
  - **Deps:** ~~4.3~~, ~~4.5~~

---

## Phase 5 — Filtering & Search

- [ ] **5.1** Add query params to `GET /v1/cards` (`name`, `set`, `type`, `rarity`, `supertype`, `sort`, `page_size`, `page_token`)
  - **Deps:** ~~2.7~~

- [ ] **5.2** Write `firestore.indexes.json` — composite indexes: (set_id + number), (types + rarity), (name + set_id)
  - **Deps:** ~~5.1~~
  - **Blockers:** Live Firestore instance required for index deployment

- [ ] **5.3** Write filter combination tests
  - **Deps:** ~~5.1~~, ~~5.2~~

---

## Phase 6 — Variants

- [ ] **6.1** Write `GET /v1/cards/{cardId}/variants` — returns `CardVariantResolved` list with `effective_image_url` (fallback to parent if variant `image_url` is null; auth required)
  - **Deps:** ~~2.8~~

- [ ] **6.2** Write `POST /v1/admin/cards/{cardId}/variants` — optional image; if no image `image_url=null` (falls back to parent); validates parent card has non-null `image_url`
  - **Deps:** ~~3.6~~

- [ ] **6.3** Write `PUT /v1/admin/cards/{cardId}/variants/{variantId}` — partial update; optionally replace image; explicitly setting `image_url=null` allowed (reverts to fallback)
  - **Deps:** ~~6.2~~

- [ ] **6.4** Write `DELETE /v1/admin/cards/{cardId}/variants/{variantId}` — delete Firestore doc; delete GCS image only if `image_url` non-null
  - **Deps:** ~~6.2~~

- [ ] **6.5** Write tests (create with/without image, `effective_image_url` resolution, update add/remove image, delete GCS only when image existed, 400 if parent has no image)
  - **Deps:** ~~6.1~~, ~~6.2~~, ~~6.3~~, ~~6.4~~

---

## Phase S — Data Scraper & Import Pipeline (Independent)

> `scripts/scraper/` committed; `scripts/scraper/data/` gitignored.
> Source: TCGDex (`https://api.tcgdex.net/v2/{lang}/`) — free, MIT, no auth.
> Upload: via admin API. Skip existing by default; `--force-images` re-downloads images.

- [ ] **S.1** Create `scripts/scraper/`; add `scripts/scraper/data/` and `scripts/scraper/.env` to `.gitignore`
  - **Deps:** ~~0.2~~

- [ ] **S.2** `uv init` scraper — `httpx`, `pillow`, `pyyaml`, `click`, `python-dotenv`; dev: `pytest`, `pytest-asyncio`, `respx`
  - **Deps:** ~~S.1~~

- [ ] **S.3** Write `tcgdex_client.py` — `get_all_sets`, `get_set`, `get_cards_in_set`, `get_card` (all per lang), `download_image` (streams, skips existing), retry/backoff
  - **Deps:** ~~S.2~~

- [ ] **S.4** Write `transformer.py` — `transform_card_base`, `transform_card_translation`, `transform_set_base`, `transform_set_translation`, `extract_variants`
  - **Deps:** ~~S.3~~

- [ ] **S.5** Write `downloader.py` — per-set per-language; images only on `lang=="en"` or `--force-images`; skips existing files; progress output
  - **Deps:** ~~S.3~~, ~~S.4~~

- [ ] **S.6** Write `admin_client.py` — HTTP wrapper: `create_set`, `create_card`, `add_translation`, `create_variant`, `check_exists` (HEAD request)
  - **Deps:** ~~S.2~~

- [ ] **S.7** Write `uploader.py` — reads `data/en/`, calls admin_client; skip-existing; uploads translations from all other langs
  - **Deps:** ~~S.5~~, ~~S.6~~

- [ ] **S.8** Write `main.py` CLI — `list-sets`, `scrape [--set|--all] [--lang] [--force-images]`, `upload [--set|--all] [--env]`, `sync`, `status`
  - **Deps:** ~~S.5~~, ~~S.7~~

- [ ] **S.9** Write pytest suite (`test_transformer.py` all langs, `test_downloader.py` skip + force-images, `test_uploader.py` skip-existing + translations)
  - **Deps:** ~~S.4~~, ~~S.5~~, ~~S.7~~

- [ ] **S.10** End-to-end test: `sync --set base1 --env dev`; verify Firestore + GCS + translations; re-run `--force-images`
  - **Deps:** ~~S.8~~, ~~S.9~~, ~~3.12~~
  - **Blockers:** `make dev` running

---

## Phase 7 — Production & Polish

- [ ] **7.1** Write `terraform/environments/prod/` (same structure as dev, separate state prefix)
  - **Deps:** ~~1.7~~

- [ ] **7.2** Set up custom domain — Cloudflare CNAME → GCP Cloud Run domain mapping (`google_cloud_run_domain_mapping`)
  - **Deps:** ~~1.7~~
  - **Blockers:** Domain name decided; Cloudflare account access

- [ ] **7.3** Update CORS for production (env var: prod sets explicit `https://api.{domain}`, not `*`)
  - **Deps:** ~~7.2~~

- [ ] **7.4** Add OpenAPI customisation (title, server URL, tags, "shown once" warnings on key endpoints)
  - **Deps:** ~~2.11~~, ~~3.13~~

- [ ] **7.5** Add rate limit response headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
  - **Deps:** ~~2.4~~

- [ ] **7.6** Tighten GCS CORS to production domain only (update `modules/storage/` CORS from `*`)
  - **Deps:** ~~7.2~~

- [ ] **7.7** Write `README.md` (API overview, auth guide, local dev, contribution guide, link to `/docs`)
  - **Deps:** Phase 2 done, Phase 3 done

---

## Phase D — API Documentation

> All docs live under `docs/`. OpenAPI auto-docs served at `/docs` and `/redoc` by FastAPI.

- [ ] **D.1** Enhance OpenAPI metadata — title, version, description, server URLs, contact, license; add `summary` + `description` to every endpoint
  - **Deps:** ~~2.11~~, ~~3.13~~
  - Note: supersedes 7.4

- [ ] **D.2** Write `docs/authentication.md` — invite code flow, key format, rotation, revocation, "shown once" warning

- [ ] **D.3** Write `docs/rate-limiting.md` — tier table (owner/premium/standard), quota reset window, 429 response shape, `X-RateLimit-*` headers

- [ ] **D.4** Write `docs/errors.md` — all HTTP status codes used, standard `ErrorResponse` shape, common causes (401 vs 403, 404 vs 422)

- [ ] **D.5** Write `docs/cards.md` + `docs/sets.md` — field-level reference for Card and CardSet schemas; translation fallback behaviour; variant image resolution rules

- [ ] **D.6** Write `docs/quickstart.md` — end-to-end: get invite code → register key → first API call → pagination example (curl + Python snippets)

- [ ] **D.7** Write `CHANGELOG.md` — initial entry for v0.1.0 covering Phase 2 + 2.5 endpoints
  - **Deps:** Phase 2 done, Phase 2.5 done

---

## Phase SDK-Py — Python SDK (`sdks/python/`)

> Typed Python client library. Published to PyPI as `nottcreature`.

- [ ] **Py.1** `uv init` — deps: `httpx`; dev: `pytest`, `pytest-asyncio`, `respx`
  - **Deps:** ~~2.5~~

- [ ] **Py.2** Write `NottClient` — API key header, base URL config, timeout
  - **Deps:** ~~Py.1~~

- [ ] **Py.3** Write typed models (`Card`, `CardSummary`, `CardSet`, `ApiKey`, `PaginatedResponse[T]`) mirroring public-api shapes
  - **Deps:** ~~Py.1~~

- [ ] **Py.4** Write `cards` + `sets` + `keys` sub-clients (list, get, async pagination iterator)
  - **Deps:** ~~Py.2~~, ~~Py.3~~

- [ ] **Py.5** 429 retry with exponential backoff; map HTTP errors → typed exceptions (`NottApiError`, `UnauthorizedError`, `RateLimitError`)
  - **Deps:** ~~Py.2~~

- [ ] **Py.6** pytest suite with `respx` mocks — list, get, pagination, 401, 429 retry
  - **Deps:** ~~Py.4~~, ~~Py.5~~

- [ ] **Py.7** `pyproject.toml` publish config + `README.md` with quickstart
  - **Deps:** ~~Py.6~~

- [ ] **Py.8** Publish to PyPI
  - **Deps:** ~~Py.7~~
  - **Blockers:** PyPI account; stable public API URL

---

## Phase SDK-JS — JavaScript/TypeScript SDK (`sdks/typescript/`)

> Typed TypeScript client library. Published to npm as `nottcreature`.

- [ ] **JS.1** `npm init` — TypeScript, native `fetch`; dev: `jest`, `msw`, `ts-jest`
  - **Deps:** ~~2.5~~

- [ ] **JS.2** Write `NottClient` class — API key header, base URL, timeout
  - **Deps:** ~~JS.1~~

- [ ] **JS.3** Write TypeScript interfaces (`Card`, `CardSummary`, `CardSet`, `ApiKey`, `PaginatedResponse<T>`)
  - **Deps:** ~~JS.1~~

- [ ] **JS.4** Write `cards` + `sets` + `keys` modules (list, get, async pagination iterator)
  - **Deps:** ~~JS.2~~, ~~JS.3~~

- [ ] **JS.5** 429 retry with backoff; typed error classes (`NottApiError`, `UnauthorizedError`, `RateLimitError`)
  - **Deps:** ~~JS.2~~

- [ ] **JS.6** Jest tests with `msw` handlers — list, get, pagination, 401, 429 retry
  - **Deps:** ~~JS.4~~, ~~JS.5~~

- [ ] **JS.7** `package.json` publish config + `tsconfig.json` + `README.md`
  - **Deps:** ~~JS.6~~

- [ ] **JS.8** Publish to npm
  - **Deps:** ~~JS.7~~
  - **Blockers:** npm account; stable public API URL

---

## Phase SDK-Java — Java SDK (`sdks/java/`)

> Typed Java client library. Published to Maven Central as `io.nottcreature:client`.

- [ ] **Java.1** Gradle init — deps: `OkHttp`, `Jackson`; test: `JUnit 5`, `WireMock`
  - **Deps:** ~~2.5~~

- [ ] **Java.2** Write `NottClient` builder (`apiKey`, `baseUrl`, `timeout`)
  - **Deps:** ~~Java.1~~

- [ ] **Java.3** Write POJOs / Java records (`Card`, `CardSummary`, `CardSet`, `ApiKey`, `PaginatedResponse<T>`) with Jackson annotations
  - **Deps:** ~~Java.1~~

- [ ] **Java.4** Write `CardsClient` + `SetsClient` + `KeysClient` (list, get, pagination)
  - **Deps:** ~~Java.2~~, ~~Java.3~~

- [ ] **Java.5** 429 retry with backoff; exception hierarchy (`NottApiException`, `UnauthorizedException`, `RateLimitException`)
  - **Deps:** ~~Java.2~~

- [ ] **Java.6** JUnit 5 + WireMock tests — list, get, pagination, 401, 429 retry
  - **Deps:** ~~Java.4~~, ~~Java.5~~

- [ ] **Java.7** `build.gradle` publish config + `README.md`
  - **Deps:** ~~Java.6~~

- [ ] **Java.8** Publish to Maven Central
  - **Deps:** ~~Java.7~~
  - **Blockers:** Sonatype account; stable public API URL

---

## Phase W — Web Admin UI (Stretch Goal)

> Vue 3 + Vite + TypeScript. Firebase Auth (Google sign-in, owner email check). Admin API key via Firebase Remote Config. Staged-edit publish workflow.

- [ ] **W.1** Add Firebase project + Hosting + Remote Config to Terraform (`terraform/modules/firebase/`)
  - **Deps:** ~~1.3~~

- [ ] **W.2** Configure Firebase Auth (Google sign-in; owner email check in `auth.ts`)
  - **Deps:** ~~W.1~~

- [ ] **W.3** `npm create vite@latest` Vue 3 + TS; add `pinia`, `vue-router`, `firebase`, `axios`, `@vueuse/core`
  - **Deps:** ~~0.2~~

- [ ] **W.4** Write `lib/firebase.ts` (init with `VITE_*` env placeholders; export `auth`, `remoteConfig`)
  - **Deps:** ~~W.3~~

- [ ] **W.5** Write auth store + `LoginView.vue` + router guard (owner email check; fetch Remote Config post-auth)
  - **Deps:** ~~W.4~~

- [ ] **W.6** Write `lib/adminApi.ts` + `lib/publicApi.ts` (typed axios; keys/URLs from Remote Config)
  - **Deps:** ~~W.5~~

- [ ] **W.7** Write staging store (`stores/staging.ts` — Pinia, localStorage; per-op status `pending|in_flight|done|error`)
  - **Deps:** ~~W.6~~

- [ ] **W.8** Write `StagingDrawer.vue` (fixed diff drawer, Publish All + Discard All)
  - **Deps:** ~~W.7~~

- [ ] **W.9** Write `SetsView.vue` + `SetEditForm.vue` (grid + edit; stages changes)
  - **Deps:** ~~W.6~~, ~~W.7~~

- [ ] **W.10** Write `CardsView.vue` + `SearchBar.vue` + `FilterPanel.vue` (thumbnail grid + search + type/rarity filters)
  - **Deps:** ~~W.6~~

- [ ] **W.11** Write `CardDetailView.vue` + `CardEditForm.vue` (all metadata fields staged)
  - **Deps:** ~~W.7~~, ~~W.10~~

- [ ] **W.12** Write `AttackEditor.vue` + `AbilityEditor.vue` (inline list CRUD, reorderable rows)
  - **Deps:** ~~W.11~~

- [ ] **W.13** Write `TranslationEditor.vue` (tab per language, editable localised fields, staged)
  - **Deps:** ~~W.11~~

- [ ] **W.14** Write `ImageUploader.vue` (drag-and-drop; preview before staging; publishes via `PUT /v1/admin/cards/{id}/image`)
  - **Deps:** ~~W.11~~

- [ ] **W.15** Write `VariantManager.vue` (list + add optional image + delete; staged)
  - **Deps:** ~~W.11~~

- [ ] **W.16** Write `KeysView.vue` — `KeyDashboard.vue` + `InviteCodeManager.vue`
  - **Deps:** ~~W.6~~

- [ ] **W.17** Write `ScraperView.vue` + `ScraperPanel.vue` (trigger Cloud Run Job, poll status)
  - **Deps:** ~~W.6~~, ~~3.13~~

- [ ] **W.18** Admin API: `POST /v1/admin/scraper/jobs` — triggers Cloud Run Job for scraper
  - **Deps:** ~~3.13~~

- [ ] **W.19** Write `firebase.json` (SPA rewrite) + `vite.config.ts` (`VITE_*` prefix)
  - **Deps:** ~~W.3~~

- [ ] **W.20** Add `deploy-admin-ui` GitHub Actions job (`npm run build` → `firebase deploy --only hosting`)
  - **Deps:** ~~W.19~~, ~~4.3~~

- [ ] **W.21** End-to-end test: sign in → edit card → stage → publish → verify via public API
  - **Deps:** ~~W.8~~, ~~W.11~~, ~~3.11~~

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Region | `us-central1` | Cheapest for Firestore + Cloud Run |
| DNS | Cloudflare | Custom domain via CNAME to Cloud Run |
| Rate limit store | In-memory (slowapi) | Zero cost; good enough for v1 |
| API key signup | Invite-code gated | Owner controls who gets access |
| Key tiers | owner / premium / standard | Configurable via `limits.yaml` |
| Scraper image updates | Skip by default, `--force-images` re-downloads | Preserves manual edits |
| Translations | Map field on card doc | No subcollection overhead |
| Variant images | Optional, fallback to parent `image_url` | Register variant before image is ready |
| Logging | Structured JSON to stdout | Free, picked up by Cloud Logging |

---

## Currently Unblocked

- ~~**0.1–0.6**~~ ✓ Phase 0 complete
- ~~**2.0–2.0d**~~ ✓ Public API bootstrap complete
- ~~**2.1–2.14**~~ ✓ Phase 2 complete (public API, all tests green)
- ~~**2.5.1–2.5.8**~~ ✓ Phase 2.5 complete (key management, 23 tests green)
- ~~**1.0–1.7**~~ ✓ Terraform written; `terraform validate` passes
- **1.8** — `terraform plan` (Blocker: real GCP project + bootstrap bucket)
- **3.0–3.0c** — `uv init` admin-api + config + logging + env
- **S.1** — scraper dir setup (fully independent)
