COMPOSE_SERVICE=flask-app
MCP_SERVICE=mcp-server
DB_PATH=/app/data/bball.db

.PHONY=build up down restart ps flask mcp swagger interactive notebook \
	db_clean db_create db_load db_rm db_interactive \
	autodoc test logs logs-flask logs-mcp logs-swagger \
	mcp-test mcp-interactive

# Docker Compose Management
build: ## Build all Docker images
	docker compose build

up: build ## Start all services in detached mode
	docker compose up -d

down: ## Stop and remove all containers
	docker compose down

restart: down up ## Restart all services

# Flask Service Commands
flask: build ## Start Flask app only
	docker compose up flask-app

interactive: build ## Open bash shell in Flask container
	docker compose run --rm $(COMPOSE_SERVICE) /bin/bash

notebook: build ## Run Jupyter notebook server (port 8888)
	docker compose run --rm -p 8888:8888 $(COMPOSE_SERVICE) \
		uv run jupyter notebook --allow-root --no-browser \
		--port 8888 --ip=0.0.0.0

mcp-interactive: build ## Open bash shell in MCP server container
	docker compose run --rm $(MCP_SERVICE) /bin/bash

# Database Commands
db_create: build ## Create database schema
	docker compose run --rm flask-app \
		uv run python /app/app/data_utils/db_manage.py db_create

db_load: build ## Load data into database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_load

db_rm: build ## Remove all data from database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_rm

db_clean: build ## Clean the database
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run python /app/app/data_utils/db_manage.py db_clean

db_interactive: build ## Open interactive SQLite shell
	docker compose run --rm -it $(COMPOSE_SERVICE) \
		sqlite3 -column -header $(DB_PATH)

# Documentation and Testing
autodoc: build ## Serve MkDocs documentation (port 4040)
	docker compose run --rm -p 4040:4040 $(COMPOSE_SERVICE) \
		uv run mkdocs serve --dev-addr 0.0.0.0:4040 -f /app/api-docs/mkdocs.yml

test: build ## Run pytest with coverage
	docker compose run --rm $(COMPOSE_SERVICE) \
		uv run pytest --cov=app /app/test/test.py --cov-report=term-missing -v

swagger: ## Start Swagger UI only
	docker compose up swagger-ui

# Logging
logs: ## Show logs from all services
	docker compose logs -f

logs-flask: ## Show logs from Flask app only
	docker compose logs -f flask-app

logs-mcp: ## Show logs from MCP server only
	docker compose logs -f mcp-server

logs-swagger: ## Show logs from Swagger UI only
	docker compose logs -f swagger-ui

# Combined Commands
start-all: build ## Start Flask, MCP, and Swagger services
	docker compose up -d flask-app mcp-server swagger-ui

stop-all: ## Stop all services
	docker compose down

clean: down ## Remove all containers, networks, and volumes
	docker compose down -v
	docker system prune -f

