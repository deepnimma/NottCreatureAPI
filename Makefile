.PHONY: dev dev-build test lint format tf-plan-dev tf-apply-dev tf-destroy-dev build

# ── Local dev ──────────────────────────────────────────────────────────────────

dev:
	docker compose watch

dev-build:
	docker compose up --build

down:
	docker compose down -v

# ── Tests & linting ────────────────────────────────────────────────────────────

test:
	cd services/public-api  && uv run pytest tests/ -v
	cd services/admin-api   && uv run pytest tests/ -v

lint:
	uv run ruff check services/
	uv run mypy services/public-api/app services/admin-api/app

format:
	uv run ruff format services/
	uv run ruff check --fix services/

# ── Docker builds ──────────────────────────────────────────────────────────────

build:
	docker build -t public-api:local  services/public-api
	docker build -t admin-api:local   services/admin-api

# ── Terraform (dev) ────────────────────────────────────────────────────────────

tf-init-dev:
	cd terraform/environments/dev && terraform init

tf-plan-dev:
	cd terraform/environments/dev && terraform plan

tf-apply-dev:
	cd terraform/environments/dev && terraform apply

tf-destroy-dev:
	cd terraform/environments/dev && terraform destroy

# ── Terraform (bootstrap) ──────────────────────────────────────────────────────

tf-bootstrap:
	cd terraform/bootstrap && terraform init && terraform apply
