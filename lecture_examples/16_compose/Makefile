COMPOSE_SERVICE=flask-app
DB_PATH=/app/data/bball.db

.PHONY=help build up down restart ps flask swagger interactive notebook \
	db_clean db_create db_load db_rm db_interactive \
	autodoc test logs logs-flask logs-swagger

.DEFAULT_GOAL := help

# Docker Compose Management
build: ## Build all Docker images
	docker compose build

up: build ## Start all services in detached mode
	docker compose up -d

down: ## Stop and remove all containers
	docker compose down

ps: ## Show running containers
	docker ps --filter "name=bball"

interactive: ## Open bash shell in Flask container
	docker compose run --rm $(COMPOSE_SERVICE) /bin/bash

notebook: ## Run Jupyter notebook server (port 8888)
	docker compose run --rm -p 8888:8888 $(COMPOSE_SERVICE) \
		uv run jupyter notebook --allow-root --no-browser \
		--port 8888 --ip=0.0.0.0

# Database Commands
db_create: ## Create database schema
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_create

db_load: ## Load data into database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_load

db_rm: ## Remove all data from database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_rm

db_clean: ## Clean the database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_clean

db_interactive: ## Open interactive SQLite shell
	docker compose run --rm -it $(COMPOSE_SERVICE) \
		sqlite3 -column -header $(DB_PATH)

# Documentation and Testing
autodoc: ## Serve MkDocs documentation (port 4040)
	docker compose run --rm -p 4040:4040 $(COMPOSE_SERVICE) \
		uv run mkdocs serve --dev-addr 0.0.0.0:4040 -f /app/api-docs/mkdocs.yml

test: ## Run pytest with coverage
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run pytest --cov=app /app/test/test.py --cov-report=term-missing -v

# Logging
logs: ## Show logs from all services
	docker compose logs -f

logs-flask: ## Show logs from Flask app only
	docker compose logs -f flask-app

logs-swagger: ## Show logs from Swagger UI only
	docker compose logs -f swagger-ui