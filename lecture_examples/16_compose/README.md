# Basketball API with Docker Compose

This repository demonstrates a Flask API with automatic OpenAPI documentation using flask-openapi3 and Swagger UI.

## Project Structure

- `flask_app/` - Flask application code
- `pyproject.toml` - Python dependencies
- `docker-compose.yml` - Docker Compose configuration
- `Makefile` - Convenient commands for common tasks

## Quick Start

### Build and run all services (Flask API + Swagger UI):
```bash
make build
make swagger
```

The API will be available at `http://localhost:4000`

### Available Documentation UIs:

**Built-in UIs (served by Flask app):**
- Swagger UI: `http://localhost:4000/docs/swagger`
- ReDoc: `http://localhost:4000/docs/redoc`
- RapiDoc: `http://localhost:4000/docs/rapidoc`
- RapiPDF: `http://localhost:4000/docs/rapipdf`
- Scalar: `http://localhost:4000/docs/scalar`
- Elements: `http://localhost:4000/docs/elements`

**Separate Container UI:**
- Swagger UI (standalone): `http://localhost:8080`

### Run only the Flask API:
```bash
make flask
```

### Common Commands

Run `make help` to see all available commands, or use these common ones:

**Docker Management:**
- `make build` - Build all Docker images
- `make up` - Start all services in detached mode
- `make down` - Stop and remove all containers
- `make restart` - Restart all services
- `make ps` - Show running containers

**Running Services:**
- `make flask` - Run Flask API only (foreground)
- `make swagger` - Run Flask API + Swagger UI (foreground)
- `make interactive` - Open bash shell in Flask container

**Database Operations:**
- `make db_create` - Create database schema
- `make db_load` - Load data into database
- `make db_rm` - Remove all data
- `make db_clean` - Clean the database
- `make db_interactive` - Open interactive SQLite shell

**Development Tools:**
- `make notebook` - Run Jupyter notebook (port 8888)
- `make autodoc` - Serve MkDocs documentation (port 4040)
- `make test` - Run pytest with coverage

**Logging:**
- `make logs` - Show logs from all services
- `make logs-flask` - Show logs from Flask app only
- `make logs-swagger` - Show logs from Swagger UI only

## API Endpoints

The API provides endpoints for:
- **Players**: List, add, delete, and get player information
- **Teams**: List players by team
- **Colleges**: List colleges and filter by team

All endpoints are automatically documented via OpenAPI/Swagger.

## Technologies

- Flask with flask-openapi3 for automatic API documentation
- Docker Compose for multi-container orchestration
- Swagger UI for interactive API documentation
- SQLite for data storage
- uv for Python package management

**NOTE** This is not "good" code. It is for demonstration purposes only.