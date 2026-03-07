# =============================================================================
# Showcase — Makefile
# =============================================================================
# Common commands for development and deployment.
#
# Usage:
#   make dev        — Start all services with Docker Compose (dev)
#   make prod       — Start all services with Docker Compose (prod)
#   make migrate    — Run Django migrations
#   make superuser  — Create a Django superuser
#   make seed       — Bootstrap members from GitHub org
#   make sync       — Sync repos + contributions + recalculate scores
#   make shell      — Open Django shell
#   make test       — Run Django tests
# =============================================================================

.PHONY: help dev dev-down prod prod-down migrate superuser seed sync shell test lint logs

# Default target
help:
	@echo "Available commands:"
	@echo "  make dev          Start development environment (Docker)"
	@echo "  make dev-down     Stop development environment"
	@echo "  make prod         Start production environment (Docker)"
	@echo "  make prod-down    Stop production environment"
	@echo "  make migrate      Run database migrations"
	@echo "  make superuser    Create a Django admin superuser"
	@echo "  make seed         Bootstrap members from GitHub org"
	@echo "  make sync         Full sync: repos + contributions + scores"
	@echo "  make shell        Open Django interactive shell"
	@echo "  make test         Run Django tests"
	@echo "  make logs         Tail Docker Compose logs"

# ---------------------------------------------------------------------------
# Docker Compose — Development
# ---------------------------------------------------------------------------
dev:
	docker compose up --build

dev-down:
	docker compose down

# ---------------------------------------------------------------------------
# Docker Compose — Production
# ---------------------------------------------------------------------------
prod:
	docker compose -f docker-compose.prod.yml up --build -d

prod-down:
	docker compose -f docker-compose.prod.yml down

# ---------------------------------------------------------------------------
# Django management commands (run inside Docker)
# ---------------------------------------------------------------------------
migrate:
	docker compose exec backend python manage.py migrate --noinput

superuser:
	docker compose exec backend python manage.py createsuperuser

seed:
	docker compose exec backend python manage.py seed_members

sync:
	docker compose exec backend python manage.py seed_members --sync

shell:
	docker compose exec backend python manage.py shell

test:
	docker compose exec backend python manage.py test

# ---------------------------------------------------------------------------
# Django management commands (local — no Docker)
# ---------------------------------------------------------------------------
local-migrate:
	cd backend && python manage.py migrate --noinput

local-superuser:
	cd backend && python manage.py createsuperuser

local-seed:
	cd backend && python manage.py seed_members

local-sync:
	cd backend && python manage.py seed_members --sync

local-shell:
	cd backend && python manage.py shell

local-test:
	cd backend && python manage.py test

local-run:
	cd backend && python manage.py runserver 0.0.0.0:8000

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-celery:
	docker compose logs -f celery-worker celery-beat
