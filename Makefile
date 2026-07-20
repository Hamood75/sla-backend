# Makefile for Street Labs Africa backend
# Docker compose helpers and deploy shortcuts

.PHONY: help build up up-logs down logs shell shell-db migrate migrations seed superuser test static clean deploy release push

COMPOSE := $(shell if docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)
APP = web
DB = db
IMAGE ?= streetlabsafrica/sla-backend:latest

help:
	@echo "Available targets:"
	@echo "  build        - Build Docker images"
	@echo "  up           - Start services in detached mode"
	@echo "  up-logs      - Start services with logs attached"
	@echo "  down         - Stop services"
	@echo "  logs         - Follow container logs"
	@echo "  shell        - Open a shell in the web container"
	@echo "  shell-db     - Open a shell in the Postgres container"
	@echo "  migrate      - Run Django migrations"
	@echo "  migrations   - Make Django migrations"
	@echo "  seed         - Seed platform test data"
	@echo "  superuser    - Create a superuser"
	@echo "  test         - Run Django tests"
	@echo "  static       - Collect static files"
	@echo "  clean        - Stop services and remove volumes/images"
	@echo "  deploy       - Build and start services, then migrate"
	@echo "  release      - Build and push Docker image"
	@echo "  push         - Alias for release"

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

migrate:
	$(COMPOSE) exec $(APP) python manage.py migrate

migrations:
	$(COMPOSE) exec $(APP) python manage.py makemigrations

seed:
	$(COMPOSE) exec $(APP) python manage.py seed_platform

superuser:
	$(COMPOSE) exec $(APP) python manage.py createsuperuser

test:
	$(COMPOSE) exec $(APP) python manage.py test

static:
	$(COMPOSE) exec $(APP) python manage.py collectstatic --noinput

clean:
	$(COMPOSE) down -v
	docker system prune -f

deploy:
	$(COMPOSE) up -d --build
	$(COMPOSE) exec $(APP) python manage.py migrate

release:
	docker build -t $(IMAGE) .
	docker push $(IMAGE)

push: release
