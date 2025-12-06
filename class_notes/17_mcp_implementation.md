<!---
title: "MCP Implementation"
--->

# MCP Implementation: Building a Multi-Service System

## Overview

In this lecture, we'll build a complete MCP server implementation using the basketball API example. This is a **multi-service system** that consists of:

1. **Flask API** - RESTful API serving basketball data
2. **MCP Server** - Exposes Flask API functionality as MCP tools
3. **Swagger UI** - Interactive API documentation

We'll focus heavily on **Docker Compose** because managing multiple services requires understanding how they start, stop, communicate, and can be monitored independently.

We will turn our previous project (the one found [here](../lecture_examples/16_compose/)) into one that uses MCP in order to communicate with our basketball API.


## Getting MCP Up and Running: Step-by-Step

This section walks you through converting your existing Flask project to use MCP with Docker Compose.

**Overview of steps:**
1. Reorganize Flask Project Structure:  Reorganize project structure, move all specific service information to a subdirectory. `Dockerfile` and `pyproject.toml` should not be in the top level.
2. Create an MCP server directory
3. Create a new `Dockerfile`, `pyproject.toml` and python scripts for running your server. 
4. Create a docker-compose.yml
5. Update Makefile to use Docker Compose rather than just docker

**Summary of what is created:**

```
my_project/
├── docker-compose.yml       # ← Orchestrates all services
├── Makefile                 # ← Updated to use docker compose
├── flask_app/               # ← Existing Flask code
│   ├── Dockerfile
│   ├── app.py
│   └── ...
└── mcp_server/              # ← New MCP server
    ├── Dockerfile           # ← Created
    ├── pyproject.toml       # ← Created
    ├── server.py            # ← Created
    ├── tools.py             # ← Created
    └── models.py            # ← Created (type aliases for responses)
```

## Docker Compose Configuration

Let's examine the `docker-compose.yml` file piece by piece:

**Flask service:**
```yaml
services:
  flask-app:
    build:
      context: ./flask_app
      dockerfile: Dockerfile
    container_name: bball_flask_app
    ports:
      - "4000:5000"
    volumes:
      - ./flask_app:/app
    environment:
      - DB_PATH=/app/data/bball.db
      - DATA_DIR=/app/data
    networks:
      - bball-network
```

**Key points:**
- `build.context`: Where to find the Dockerfile
- `container_name`: Fixed name for easy reference
- `ports`: "host:container" - host port 4000 maps to container port 5000
- `volumes`: Mount local directories into container (for development)
- `environment`: Pass environment variables to the container
- `networks`: Connects to the shared network

**MCP Server service:**
```yaml
  mcp-server:
    build:
      context: ./mcp_server
      dockerfile: Dockerfile
    container_name: bball_mcp_server
    ports:
      - "3000:3000"
    volumes:
      - ./mcp_server:/app
    environment:
      - FLASK_API_URL=http://flask-app:5000
    command: ["uv", "run", "server.py"]
    depends_on:
      - flask-app
    networks:
      - bball-network
```

**Critical differences:**
- `volumes`: Mounts local code for live development (changes without rebuilding)
- `command`: Specifies how to run the server (using `uv run`)
- `depends_on`: Flask must be started first
- `FLASK_API_URL=http://flask-app:5000`: Uses the **service name** as hostname


**Swagger UI service:**
```yaml
  swagger-ui:
    image: swaggerapi/swagger-ui:latest
    container_name: bball_swagger_ui
    ports:
      - "8081:8080"
    environment:
      - SWAGGER_JSON_URL=http://localhost:4000/docs/openapi.json
    depends_on:
      - flask-app
    networks:
      - bball-network

networks:
  bball-network:
    driver: bridge
```

**Additional service:**
- Uses a pre-built image (not built locally)
- Depends on Flask but doesn't need health check
- All services share the `bball-network` network

## Docker Networks and Service Discovery

When services are on the same Docker network, they can communicate using **service names as hostnames**:

```
mcp-server wants to reach flask-app:
  URL: http://flask-app:5000/api/players
       └─── service name from docker-compose.yml
```

**From outside Docker** (your browser or curl):
```
http://localhost:4000/api/players
       └─── mapped host port
```

**This is crucial**: Services talk to each other using internal service names and ports. You access them from your host machine using mapped ports.

## Starting the System

**Build all images:**
```bash
make build
```

This builds Docker images for `flask-app` and `mcp-server` based on their respective Dockerfiles.

- Docker reads each service's `Dockerfile`
- Installs dependencies
- Creates images tagged for this project
- Swagger UI is skipped (uses pre-built image)

**Start services together:**
```bash
make start-all
```

The `-d` flag runs services in "detached" mode (background).

What happens:
1. Docker creates the `bball-network` network
2. Starts `flask-app` first
3. Starts `mcp-server` (depends on flask-app)
4. Starts `swagger-ui` (depends on flask-app)

**Check running services:**
```bash
docker ps
```

Output:
```
CONTAINER ID   IMAGE              STATUS          PORTS                    NAMES
a1b2c3d4e5f6   17_mcp-flask-app   Up 2 minutes   0.0.0.0:4000->5000/tcp   bball_flask_app
b2c3d4e5f6g7   17_mcp-mcp-server  Up 1 minute    0.0.0.0:3000->3000/tcp   bball_mcp_server
c3d4e5f6g7h8   swagger-ui         Up 1 minute    0.0.0.0:8081->8080/tcp   bball_swagger_ui
```

## Managing Services

**Starting services one at a time:**

- **Start only Flask:** `make flask` - Runs in foreground, see logs in real-time. Press `Ctrl+C` to stop.
- **Start only MCP server:** `make mcp`

**Stopping services:**

- **Stop all services:** `make stop-all`

## Viewing Logs

One of the most important skills is **reading logs** to understand what's happening in each service.

**View all logs together:**
```bash
make logs
```

The `-f` flag "follows" logs (like `tail -f`). Output shows **which service** each log comes from:
```
bball_flask_app    | INFO:     Started server process [1]
bball_mcp_server   | INFO:     Waiting for Flask API to be ready...
bball_swagger_ui   | Listening on port 8080
```

**View individual service logs:**

- **Flask only:** `make logs-flask` or `docker compose logs -f flask-app`
- **MCP only:** `make logs-mcp` or `docker compose logs -f mcp-server`
- **Swagger only:** `make logs-swagger` or `docker compose logs -f swagger-ui`

**Reading logs to debug issues:**

Flask logs show:
- HTTP requests received
- Database queries
- Errors in API endpoints

MCP logs show:
- Tool executions
- Requests to Flask API
- Connection status

## Database Operations

The Flask service contains the database. Database commands run **inside the Flask container**:

```bash
make db_create
# Runs: docker compose run --rm flask-app uv run python db_manage.py db_create
```

What this does:
1. Starts a new Flask container
2. Runs the command inside it
3. `--rm` removes the container when done
4. Creates database tables

**Other database commands:**
- `make db_load` - Load data
- `make db_clean` - Clean tables
- `make db_rm` - Remove all data

**Interactive database access:**
```bash
make db_interactive
# Opens SQLite shell inside Flask container
```

## MCP Server Implementation

The MCP server uses **FastMCP**, a common framework for building MCP Servers. The `server.py` file imports the `mcp` instance from `tools.py` (which already has all tools registered) and runs it:

**server.py:**
```python
import logging
from tools import mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Basketball API MCP Server (HTTP/SSE mode)")
    mcp.run(transport="sse", host="0.0.0.0", port=3000)
```

Key points:
- Imports the `mcp` instance from `tools.py`
- Tools are already registered via decorators
- Runs in HTTP/SSE mode (server runs continuously on port 3000)
- AI assistants connect via URL at `http://localhost:3000/sse`
- No command-line arguments needed

**Note:** MCP servers can run in different transport modes (stdio vs HTTP/SSE). We use HTTP/SSE mode here because it's easier to debug and works well with Docker Compose. We'll explain both modes in Lecture 18.

## Tool Definitions with Decorators

Tools are defined in `tools.py` using the `@mcp.tool()` decorator pattern. We also use **type aliases** from a separate `models.py` file to document the structure of responses.

**Note:** The tool functions use `async def` and `httpx` for making HTTP requests to the Flask API. We'll explain async programming and httpx in detail in the next lecture (Lecture 18). For now, just understand that:
- Tools are async functions (they use `async def`)
- They use `httpx.AsyncClient()` to make HTTP requests
- The `await` keyword waits for the HTTP request to complete

**models.py (type aliases):**
```python
from typing import Any

# Type aliases for better readability
PlayerDict = dict[str, int | str]
PlayerInfo = dict[str, Any]  # Player information with all fields
AllPlayersResponse = dict[str, list[PlayerDict]]  # {"players": [...]}
TeamPlayersResponse = dict[str, list[PlayerDict]]  # {"LAL": [...], "BOS": [...]}
...
```

**tools.py (tools using those types):**
```python
...

mcp = FastMCP("Basketball API Server")

@mcp.tool()
async def get_all_players() -> AllPlayersResponse:
    """Get a list of all basketball players in the database.

    Players are grouped by team.

    Returns:
        AllPlayersResponse: Dictionary with "players" key containing list of player dicts
            with "id" (int) and "player_name" (str) keys.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players")
        response.raise_for_status()
        return response.json()
...

```

- The `mcp` instance is created in `tools.py`. This is similar to the flask app.
- Each tool uses the `@mcp.tool()` decorator
- Tools are automatically registered when the decorator runs
- Responses use **type aliases** from `models.py` to document structure
- FastMCP uses these type hints to build better JSON Schemas
- Tools are async functions that use `httpx` to make HTTP requests to the Flask API (see Lecture 18 for details on async/httpx)
- Type aliases make the code more readable and help FastMCP understand response structures

**How decorators register tools:**

The `@mcp.tool()` decorator automatically:
1. Extracts the function name as the tool name: `get_player_info`
2. Uses the docstring as the tool description
3. Parses the `Args:` section to document parameters
4. Uses type hints (`player_id: int`) to define parameter types
5. Registers the tool with FastMCP

**Example of what the AI sees:**

FastMCP converts our `get_player_info` function into this tool definition:

```json
{
  "name": "get_player_info",
  "description": "Get detailed information about a specific player by their ID.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "player_id": {
        "type": "integer",
        "description": "The unique ID of the player"
      }
    },
    "required": ["player_id"]
  }
}
```

The AI reads this and knows: "When the user asks about a specific player, I should call `get_player_info` with the player's ID."

## Why We Use Type Hints and Type Aliases

In our MCP tools we use **type hints** and **type aliases** to make our code clearer and easier for tools like FastMCP to work with. Type aliases are useful for MCP tools because they help the tool know exactly what to expect.

- Type hints tell Python (and FastMCP) what types our inputs and outputs should be.
- FastMCP uses these hints to build JSON Schemas for tool parameters and results.
- Clear types make it easier for AI assistants to call tools correctly.

In `models.py` and `tools.py` we use:

- Type aliases to document dictionary structures:
  - `PlayerDict = dict[str, int | str]` - simple player dict with id and name
  - `PlayerInfo = dict[str, Any]` - detailed player information (all fields)
  - `AllPlayersResponse = dict[str, list[PlayerDict]]` - response with "players" key
  - `AddPlayerResponse = dict[str, Any]` - response with "message" and "player" keys
  - `DeletePlayerResponse = dict[str, str]` - response with "message" key

Benefits of using type aliases in this context:

- **Self-documenting code**:
  - Inputs and outputs are clear just from the function signature.
  - Easier for humans (and AIs) to understand what the tool expects/returns.
  - Type aliases give meaningful names to dictionary structures.

- **Better tool schemas**:
  - FastMCP uses type hints to build JSON Schemas for tool parameters and results.
  - This drives how the AI constructs tool calls and interprets responses.
  - Even though we use `dict[str, Any]` for complex structures, the type alias name (`PlayerInfo`, `AddPlayerResponse`) helps document intent.

- **Safer refactoring**:
  - Static analyzers (like `ruff`, `mypy`, etc.) can catch mistakes earlier.
  - Type aliases make it easier to change structure in one place.

- **Direct JSON compatibility**:
  - Since HTTP responses return plain dictionaries, type aliases work perfectly.
  - No conversion needed - `response.json()` returns a dict that matches our type aliases.

The key idea: **use types to make tools predictable and well-documented.** We use type aliases to give FastMCP (and the AI) as much structure as possible while keeping the code simple and directly compatible with JSON responses.
