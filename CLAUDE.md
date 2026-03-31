# NottCreatureAPI

Python-based Pokemon TCG API with two services (public + admin), Firestore backend, GCS image storage, and Docker Compose local dev environment.

## Tech Stack
- **Language**: Python
- **Framework**: FastAPI
- **Database**: Firestore (emulated locally)
- **Storage**: Google Cloud Storage (emulated locally)
- **Rate limiting**: slowapi (tier-based quotas)
- **Infrastructure**: Docker Compose

## Key Commands
```bash
# Local dev (with hot-reload via docker compose watch)
make dev

# Rebuild and start
make dev-build

# Run tests
make test

# Lint + typecheck
make lint

# Tear down (removes volumes)
make down
```

## Skills
| Skill | When to use |
|---|---|
| `.claude/skills/base/skill.md` | Project structure, conventions, shared patterns |
| `.claude/skills/public-api/skill.md` | Consumer-facing API, rate limiting, Firestore reads |
| `.claude/skills/admin-api/skill.md` | Admin endpoints, GCS uploads, API key auth, Firestore writes |
| `.claude/skills/infrastructure/skill.md` | Docker Compose, emulator setup, local dev |
| `.claude/skills/rate-limiting/skill.md` | Tier config, quota rules, slowapi wiring |

## Behavior
- **Verify before claiming** — Never state that something is configured, running, scheduled, or complete without confirming it first. If you haven't verified it in this session, say so rather than assuming.
