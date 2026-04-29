.PHONY: help dev test lint type migrate up down logs shell-backend shell-db build push

help:
	@echo "make dev          - sobe stack dev (hot reload)"
	@echo "make up           - sobe stack prod local"
	@echo "make down         - derruba stack"
	@echo "make test         - roda pytest"
	@echo "make lint         - ruff check"
	@echo "make type         - mypy"
	@echo "make migrate      - alembic upgrade head"
	@echo "make shell-backend- shell no container backend"
	@echo "make shell-db     - psql no plan-trib-db"

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

up:
	docker compose up -d

down:
	docker compose down

test:
	docker compose -f docker-compose.test.yml run --rm backend pytest -v

lint:
	docker compose run --rm backend ruff check src tests

type:
	docker compose run --rm backend mypy src

migrate:
	docker compose run --rm backend alembic upgrade head

shell-backend:
	docker compose exec plan-trib-backend bash

shell-db:
	docker compose exec plan-trib-db psql -U $${DB_USER} plan_trib

logs:
	docker compose logs -f --tail=100
