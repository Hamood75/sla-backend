# Makefile for Street Labs Africa backend
# Local dev + Docker compose helpers

.PHONY: help run run-docker build up up-logs down logs shell shell-db migrate migrations seed superuser test static clean deploy release push ensure-connect-qr

COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
APP = web
DB = db
IMAGE ?= streetlabsafrica/sla-backend:latest
PORT ?= 8000

# Prefer project venv when present
PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif [ -x venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)
MANAGE := $(PYTHON) manage.py

help:
	@echo "Available targets:"
	@echo "  run               - Start Django locally on :$(PORT)"
	@echo "  migrate           - Run migrations (local, or Docker if containers are up)"
	@echo "  migrations        - Make migrations (local)"
	@echo "  seed              - Seed platform test data (local)"
	@echo "  ensure-connect-qr - Create/update SLAORG Connect QR"
	@echo "  superuser         - Create a superuser (local)"
	@echo "  test              - Run Django tests (local)"
	@echo "  build             - Build Docker images"
	@echo "  up                - Start Docker services (detached)"
	@echo "  up-logs / run-docker - Start Docker with logs"
	@echo "  down              - Stop Docker services"
	@echo "  logs              - Follow Docker logs"
	@echo "  shell             - Shell in web container"
	@echo "  deploy            - Build/start Docker + migrate"
	@echo "  release / push    - Build and push Docker image"

run:
	$(MANAGE) runserver 0.0.0.0:$(PORT)

run-docker: up-logs

migrate:
	@if $(COMPOSE) ps --status running 2>/dev/null | grep -q "$(APP)"; then \
		$(COMPOSE) exec $(APP) python manage.py migrate; \
	else \
		$(MANAGE) migrate; \
	fi

migrations:
	$(MANAGE) makemigrations

seed:
	$(MANAGE) seed_platform

ensure-connect-qr:
	$(MANAGE) ensure_connect_qr

superuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

static:
	$(MANAGE) collectstatic --noinput

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

up-logs:
	$(COMPOSE) up

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec $(APP) sh

shell-db:
	$(COMPOSE) exec $(DB) sh

clean:
	$(COMPOSE) down -v
	docker system prune -f

deploy:
	$(COMPOSE) up -d --build
	@echo "Waiting for web container to be ready..."
	@sleep 5
	@$(COMPOSE) logs --tail 20 $(APP)

release:
	docker build -t $(IMAGE) .
	docker push $(IMAGE)

push: release
