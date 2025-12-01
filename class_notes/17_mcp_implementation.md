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

## Why Docker Compose for Multi-Service Systems?

Up until now, we've been running single-container applications. But real-world systems often consist of multiple services that need to work together:

- A database service
- An API service  
- A background worker
- A monitoring service
- Documentation servers

**Docker Compose** solves this by:
- Managing multiple containers as a single application
- Defining service dependencies (Service A must start before Service B)
- Creating networks for inter-service communication
- Allowing services to find each other by name
- Starting/stopping services individually or together

## Project Structure

```
17_MCP/
├── docker-compose.yml       # Orchestrates all services
├── Makefile                 # Convenience commands
├── flask_app/               # Flask service
│   ├── Dockerfile
│   ├── flask_app.py
│   ├── app/                 # API routes, database utils
│   └── data/                # Database location
└── mcp_server/              # MCP service
    ├── Dockerfile
    ├── server.py            # Main MCP server
    └── tools.py             # Tool definitions
```

## Understanding docker-compose.yml

Let's examine the `docker-compose.yml` file piece by piece:

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
      - ${RAW_DATA_DIR}:/app/src/data/raw_data
    environment:
      - DB_PATH=/app/data/bball.db
      - DATA_241_API_KEY=${DATA_241_API_KEY}
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

```yaml
  mcp-server:
    build:
      context: ./mcp_server
      dockerfile: Dockerfile
    container_name: bball_mcp_server
    ports:
      - "3000:3000"
    environment:
      - FLASK_API_URL=http://flask-app:5000
    depends_on:
      - flask-app
    networks:
      - bball-network
```

**Critical differences:**
- `depends_on`: must be started first
- `FLASK_API_URL=http://flask-app:5000`: Uses the **service name** as hostname
- No volume mount (MCP server doesn't need live code reloading for this example)

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

## Starting the System: Step-by-Step

### Step 1: Set Environment Variables

```bash
export RAW_DATA_DIR=/path/to/your/data
export DATA_241_API_KEY=your-api-key-here
```

These are referenced in `docker-compose.yml` with `${VARIABLE_NAME}`.

### Step 2: Build All Images

```bash
make build
```

This builds Docker images for `flask-app` and `mcp-server` based on their respective Dockerfiles.

**What's happening:**
- Docker reads each service's `Dockerfile`
- Installs dependencies
- Creates images tagged for this project
- Swagger UI is skipped (uses pre-built image)

### Step 3: Start Services Together

```bash
make start-all
```

**The `-d` flag** runs services in "detached" mode (background).

**What happens:**
1. Docker creates the `bball-network` network
2. Starts `flask-app` first
3. Waits for `flask-app` to be healthy
4. Starts `mcp-server` (depends on flask-app health)
5. Starts `swagger-ui` (depends on flask-app existence)

### Step 4: Check Running Services

```bash
make ps
# or:
docker ps
```

Output:
```
CONTAINER ID   IMAGE              STATUS          PORTS                    NAMES
a1b2c3d4e5f6   17_mcp-flask-app   Up 2 minutes   0.0.0.0:4000->5000/tcp   bball_flask_app
b2c3d4e5f6g7   17_mcp-mcp-server  Up 1 minute    0.0.0.0:3000->3000/tcp   bball_mcp_server
c3d4e5f6g7h8   swagger-ui         Up 1 minute    0.0.0.0:8081->8080/tcp   bball_swagger_ui
```

## Managing Individual Services

### Starting Services One at a Time

**Start only Flask:**
```bash
make flask
```

This runs Flask in the **foreground** - you'll see logs in real-time. Press `Ctrl+C` to stop.

**Start only MCP server:**
```bash
make mcp
```

### Stopping Services

**Stop all services:**
```bash
make stop-all
```

## Viewing Logs: Understanding Different Systems

One of the most important skills is **reading logs** to understand what's happening in each service.

### View All Logs Together

```bash
make logs
```

The `-f` flag "follows" logs (like `tail -f`).

Output shows **which service** each log comes from:
```
bball_flask_app    | INFO:     Started server process [1]
bball_mcp_server   | INFO:     Waiting for Flask API to be ready...
bball_swagger_ui   | Listening on port 8080
```

### View Individual Service Logs

**Flask only:**
```bash
make logs-flask
# or:
docker compose logs -f flask-app
```

**MCP only:**
```bash
make logs-mcp
# or:
docker compose logs -f mcp-server
```

**Swagger only:**
```bash
make logs-swagger
# or:
docker compose logs -f swagger-ui
```

### Reading Logs to Debug Issues

**Flask logs** show:
- HTTP requests received
- Database queries
- Errors in API endpoints

**MCP logs** show:
- Tool executions
- Requests to Flask API
- Connection status

**Example debugging scenario:**

If MCP tools aren't working:

1. **Check if Flask is running:**
   ```bash
   docker compose ps
   ```

2. **Check Flask logs for errors:**
   ```bash
   make logs-flask
   ```

3. **Check MCP logs for connection issues:**
   ```bash
   make logs-mcp
   ```
   Look for "connection refused" or "404 Not Found"

4. **Test Flask manually:**
   ```bash
   curl http://localhost:4000/api/players
   ```

## Database Operations

The Flask service contains the database. Database commands run **inside the Flask container**:

```bash
make db_create
# Runs: docker compose run --rm flask-app uv run python db_manage.py db_create
```

**What this does:**
1. Starts a new Flask container
2. Runs the command inside it
3. `--rm` removes the container when done
4. Creates database tables

**Other database commands:**
```bash
make db_load      # Load data
make db_clean     # Clean tables
make db_rm        # Remove all data
```

**Interactive database access:**
```bash
make db_interactive
# Opens SQLite shell inside Flask container
```

## The MCP Server Implementation

The MCP server uses **FastMCP**, a common framework for building MCP Servers

```python
# server.py
from fastmcp import FastMCP
from tools import register_tools

mcp = FastMCP("Basketball API Server")
register_tools(mcp)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        mcp.run(transport="sse", host="0.0.0.0", port=3000)
    else:
        mcp.run()  # stdio mode
```

**Two transport modes:**

1. **stdio** (default): Used when AI assistant starts the server
2. **HTTP/SSE** (`--http` flag): Server runs continuously, AI connects via URL

### Tool Definitions

Tools are defined as standalone async functions in `tools.py`:

```python
async def get_all_players() -> str:
    """Get a list of all basketball players in the database.

    Players are grouped by team.
    
    Returns:
        str: Player names, IDs, and team information.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLASK_API_URL}/api/players")
        response.raise_for_status()
        result = response.json()
        return str(result)


async def get_player_info(player_id: int) -> str:
    """Get detailed information about a specific player by their ID.
    
    Args:
        player_id: The unique ID of the player
    
    Returns:
        str: Player name, team, college, and statistics.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FLASK_API_URL}/api/players/{player_id}"
        )
        response.raise_for_status()
        result = response.json()
        return str(result)
```

**Key points:**
- Each tool is a standalone `async` function
- Functions have detailed docstrings
- Makes HTTP requests to Flask API using `httpx`
- Uses `FLASK_API_URL=http://flask-app:5000` (service name)
- Returns string (AI interprets the data)

### The register_tools Function

At the end of `tools.py`, all tools are registered with the MCP server:

```python
def register_tools(mcp) -> None:
    """Register all tools with the FastMCP server.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    mcp.tool()(get_all_players)
    mcp.tool()(get_player_info)
    mcp.tool()(get_players_by_team)
    mcp.tool()(add_player)
    mcp.tool()(delete_player)
    mcp.tool()(get_players_by_college)
```

**How this works:**

1. **`mcp.tool()`** returns a decorator function
2. **`mcp.tool()(get_all_players)`** applies that decorator to the function
3. **FastMCP reads the function's metadata:**
   - Function name becomes tool name: `get_all_players`
   - Docstring becomes tool description (AI reads this!)
   - Type hints define parameter types: `player_id: int`
   - Args section in docstring describes parameters
   - Returns section describes what the tool returns

**Does MCP read the docstring?** 

**Yes!** This is crucial. FastMCP automatically:
- Extracts the main docstring text for the tool description
- Parses the `Args:` section to document parameters
- Uses type hints (`player_id: int`, `team: str`) to validate inputs
- The AI assistant reads these descriptions to decide when/how to use tools

**Example of what the AI sees:**

From our `get_player_info` function, FastMCP creates this tool definition:

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

## Understanding httpx

**What is httpx?**

`httpx` is a modern HTTP client library for Python - think of it as the async-compatible version of `requests`.

**Why not use `requests`?**

```python
# requests - synchronous, blocks
import requests
response = requests.get("http://api.example.com/data")  # Waits here
```

```python
# httpx - asynchronous, doesn't block
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get("http://api.example.com/data")  # Can do other work
```

**Key httpx features:**

1. **Async support** - Works with async/await
2. **Context manager** - Automatically manages connections
3. **Similar API to requests** - Easy to learn if you know requests

**Using httpx in our tools:**

```python
async with httpx.AsyncClient() as client:
    response = await client.get(f"{FLASK_API_URL}/api/players/{player_id}")
    response.raise_for_status()  # Raises exception if 4xx or 5xx
    result = response.json()     # Parse JSON response
    return str(result)
```

**Breaking it down:**

- `async with httpx.AsyncClient() as client:` - Creates HTTP client, closes when done
- `await client.get(...)` - Makes HTTP GET request, waits for response
- `response.raise_for_status()` - Throws error if request failed
- `response.json()` - Parses JSON response body
- `str(result)` - Converts to string for AI to read

**Common httpx methods:**

```python
# GET request
response = await client.get("http://flask-app:5000/api/players")

# POST request with JSON body
response = await client.post(
    "http://flask-app:5000/api/players",
    json={"player_name": "John Doe", "team": "LAL"}
)

# DELETE request
response = await client.delete("http://flask-app:5000/api/players/5")
```

## Async Programming in Depth

*Note: This is not on the test, but understanding async helps you write better MCP servers.*

### What Problem Does Async Solve?

**Synchronous (blocking) code:**

```python
def process_requests():
    # Request 1 arrives
    data1 = call_api()        # Wait 2 seconds
    result1 = process(data1)  # Wait 1 second
    
    # Request 2 arrives (but has to wait!)
    data2 = call_api()        # Wait 2 seconds
    result2 = process(data2)  # Wait 1 second
    
    # Total time: 6 seconds
```

**Asynchronous (non-blocking) code:**

```python
async def process_requests():
    # Request 1 arrives
    data1_task = asyncio.create_task(call_api())  # Start, don't wait
    
    # Request 2 arrives (can start immediately!)
    data2_task = asyncio.create_task(call_api())  # Start, don't wait
    
    # Now wait for both
    data1 = await data1_task  # Get result when ready
    data2 = await data2_task  # Get result when ready
    
    # Total time: ~2 seconds (both ran at same time!)
```

### The Event Loop

Async Python uses an **event loop** that manages multiple operations:

```
Event Loop:
┌─────────────────────────────────────┐
│  Task 1: Waiting for HTTP response  │
│  Task 2: Waiting for database       │
│  Task 3: Ready to run! ← Execute    │
│  Task 4: Waiting for file I/O       │
└─────────────────────────────────────┘
```

When a task is **waiting** (for network, disk, etc.), the event loop runs other tasks. This is called **cooperative multitasking**.

### Async Keywords

**`async def`** - Defines an async function (coroutine):

```python
async def my_function():
    return "result"
```

**`await`** - Waits for an async operation to complete:

```python
result = await my_function()  # Pause here until done
```

You can **only use `await` inside `async def` functions**.

**`async with`** - Async context manager:

```python
async with httpx.AsyncClient() as client:
    # Client is created
    response = await client.get("http://example.com")
    # Client is automatically closed
```

**`async for`** - Iterate over async generators (not used in our example):

```python
async for item in async_generator():
    process(item)
```

### When to Use Async

**Use async when:**
- Making HTTP requests (like our MCP tools)
- Querying databases
- Reading/writing files
- Any I/O-bound operation

**Don't use async for:**
- CPU-bound operations (calculations, data processing)
- Simple scripts that only do one thing at a time

**For MCP servers:** Async is perfect because tools often:
- Call external APIs (Flask in our case)
- Query databases
- Wait for responses

### Common Async Patterns

**Pattern 1: Making one request**

```python
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://api.example.com/data")
        return response.json()
```

**Pattern 2: Making multiple requests sequentially**

```python
async def get_player_and_team(player_id):
    async with httpx.AsyncClient() as client:
        # Get player first
        player = await client.get(f"/api/players/{player_id}")
        
        # Then get their team (needs player info)
        team = await client.get(f"/api/teams/{player.json()['team']}")
        
        return player.json(), team.json()
```

**Pattern 3: Making multiple requests concurrently**

```python
async def get_multiple_players(player_ids):
    async with httpx.AsyncClient() as client:
        # Start all requests at once
        tasks = [
            client.get(f"/api/players/{pid}")
            for pid in player_ids
        ]
        
        # Wait for all to complete
        responses = await asyncio.gather(*tasks)
        
        return [r.json() for r in responses]
```

### Debugging Async Code

**Common mistake: Forgetting `await`**

```python
# Wrong - returns coroutine object, doesn't execute
result = my_async_function()

# Right - waits for execution
result = await my_async_function()
```

**Common mistake: Using `await` outside `async def`**

```python
# Wrong - SyntaxError
def regular_function():
    result = await async_operation()

# Right - function must be async
async def async_function():
    result = await async_operation()
```

## Connecting to AI Assistants (Preview)

*Note: We'll cover this in detail in Class 18. This is a brief overview.*

Once you have your MCP server running, you can connect it to AI assistants like Claude Desktop or Cursor. There are different methods depending on whether you want the server to run continuously (HTTP/SSE) or on-demand (stdio).

### Method 1: HTTP/SSE with Direct URL (Simplest)

If your MCP server is running continuously (via `make start-all`), you can connect directly via URL.

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "basketball-api": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "basketball-api": {
      "url": "http://localhost:3000/sse",
      "description": "Basketball API MCP Server"
    }
  }
}
```

### Method 2: HTTP/SSE with mcp-remote (Claude Desktop)

`mcp-remote` is an npm package that wraps HTTP/SSE connections in a stdio interface for Claude Desktop.

**Install mcp-remote:**
```bash
npm install -g mcp-remote
```

**Configure Claude Desktop:**
```json
{
  "mcpServers": {
    "basketball-api": {
      "command": "mcp-remote",
      "args": [
        "http://localhost:3000/sse"
      ]
    }
  }
}
```

**Advantages of mcp-remote:**
- Works with Claude Desktop's stdio-based MCP client
- Still connects to HTTP server (easier to debug)
- No need to manage Docker commands in config

**Requirements:**
- Server must be running first: `make start-all`
- mcp-remote installed globally
- Claude Desktop restarted after configuration

### Method 3: stdio with Docker (On-Demand)

Have Claude Desktop/Cursor start the MCP server on-demand using Docker.

**Claude Desktop or Cursor:**
```json
{
  "mcpServers": {
    "basketball-api": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/ABSOLUTE/PATH/TO/17_MCP/docker-compose.yml",
        "run",
        "--rm",
        "mcp-server"
      ]
    }
  }
}
```

**Important notes:**
- Must use **absolute path** to docker-compose.yml
- Flask must already be running: `make flask`
- AI starts MCP when needed, stops when done
- Harder to debug (server starts/stops quickly)

### Cursor-Specific Setup

Cursor has two possible locations for MCP configuration:

**Option 1: User-level config (recommended)**
```bash
# Create/edit this file:
~/.cursor/mcp.json
```

**Option 2: Global storage**
```bash
# Alternative location:
~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json
```

**Example Cursor config (HTTP/SSE):**
```json
{
  "mcpServers": {
    "basketball-api": {
      "url": "http://localhost:3000/sse",
      "description": "Basketball API MCP Server - Query basketball player data"
    }
  }
}
```

**Steps to connect Cursor:**

1. **Start the services:**
   ```bash
   cd lecture_examples/17_MCP
   make start-all
   ```

2. **Create/edit config file:**
   ```bash
   # Create if it doesn't exist
   mkdir -p ~/.cursor
   nano ~/.cursor/mcp.json
   ```

3. **Add configuration** (see JSON above)

4. **Restart Cursor completely** (not just reload window)

5. **Verify connection:**
   - Open a new chat
   - Ask: "What MCP tools do you have available?"
   - Should see: get_all_players, get_player_info, etc.

### Claude Desktop-Specific Setup

**Configuration file location (macOS):**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Configuration file location (Windows):**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Configuration file location (Linux):**
```bash
~/.config/Claude/claude_desktop_config.json
```

**Recommended approach for Claude Desktop:**

Use **mcp-remote** for the best experience:

```json
{
  "mcpServers": {
    "basketball-api": {
      "command": "mcp-remote",
      "args": ["http://localhost:3000/sse"]
    }
  }
}
```

**Why mcp-remote for Claude Desktop?**
- Claude Desktop expects stdio-based servers
- mcp-remote bridges HTTP/SSE to stdio
- You get the debugging benefits of HTTP server
- You get the compatibility of stdio

**Complete workflow:**

1. **Install mcp-remote once:**
   ```bash
   npm install -g mcp-remote
   ```

2. **Start services:**
   ```bash
   cd lecture_examples/17_MCP
   make start-all
   ```

3. **Configure Claude Desktop** (use mcp-remote config above)

4. **Restart Claude Desktop completely**

5. **Test in Claude:**
   - Open Claude Desktop
   - Start a new conversation
   - Ask: "What tools can you use?"
   - Should list basketball API tools

### Debugging Connection Issues

**MCP tools not appearing?**

1. **Check server is running:**
   ```bash
   docker ps | grep mcp
   # Should show: bball_mcp_server
   ```

2. **Check server logs:**
   ```bash
   make logs-mcp
   # Look for startup messages
   ```

3. **Test server endpoint:**
   ```bash
   curl http://localhost:3000/sse
   # Should get SSE response headers
   ```

4. **Verify config file path:**
   ```bash
   # Claude Desktop (macOS):
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Cursor:
   cat ~/.cursor/mcp.json
   ```

5. **Check for JSON syntax errors:**
   - Missing commas
   - Incorrect quotes
   - Unclosed brackets

6. **Restart AI assistant completely:**
   - Fully quit (not just close window)
   - Relaunch application

### Comparison: HTTP/SSE vs stdio

| Aspect | HTTP/SSE | stdio |
|--------|----------|-------|
| Server lifetime | Runs continuously | Started on-demand |
| Debugging | Easy (logs always visible) | Harder (server starts/stops) |
| Port usage | Needs port 3000 | No ports needed |
| Setup complexity | Simple | More complex |
| Best for | Development, testing | Production |
| Performance | Better (server stays warm) | Slower (cold starts) |

**Recommendation for learning:** Use HTTP/SSE with `make start-all`. It's much easier to debug and monitor.

## Summary

In this lecture, we've covered:

### Docker Compose Multi-Service Systems
- How to define and manage multiple services with docker-compose.yml
- Service dependencies and Docker networks
- Starting, stopping, and monitoring services
- Viewing logs from individual services or all together

### MCP Server with FastMCP
- Building an MCP server using the FastMCP framework
- Writing async tool functions with clear docstrings
- Using the `register_tools()` pattern
- How FastMCP extracts metadata from function signatures and docstrings

### HTTP Client with httpx
- Using httpx for async HTTP requests
- Making GET, POST, and DELETE requests
- Context managers with `async with`
- Error handling with `raise_for_status()`

### Async Programming Basics
- Why MCP uses async/await (non-blocking I/O)
- Basic async syntax (`async def`, `await`)
- Common patterns and mistakes
- The event loop concept

### Tool Design
- Writing clear, descriptive docstrings (AI reads these!)
- Using type hints for parameter validation
- Structuring tools to call Flask API endpoints
- Best practices for tool naming and descriptions

### Practical Skills
- Using Makefile commands for common operations
- Debugging multi-service systems with logs
- Understanding service communication via Docker networks
- Volume mounts for live code reloading

### Connection Methods (Preview)
- HTTP/SSE with direct URL
- HTTP/SSE with mcp-remote (recommended for Claude Desktop)
- stdio with Docker (on-demand)
- Configuration file locations for Claude Desktop and Cursor

## Key Takeaways

1. **Docker Compose** is essential for managing multi-service applications
2. **Service names** act as hostnames within Docker networks
3. **FastMCP** makes it easy to create MCP servers with decorators
4. **Docstrings matter** - the AI reads them to understand your tools
5. **httpx** is the async version of requests
6. **HTTP/SSE mode** is easier to debug than stdio
7. **Volume mounts** enable live code changes without rebuilding
8. **Logs are your friend** - use them to understand what's happening

## Next Steps

In Class 18, we'll:
- Connect the MCP server to Claude Desktop and Cursor (detailed walkthrough)
- Test tool execution with real queries
- Monitor the complete request/response flow
- Debug common connection issues
- See the full system in action
- Understand how the AI interprets and uses tools

## Practice Before Next Class

1. Get the services running:
   ```bash
   cd lecture_examples/17_MCP
   make start-all
   make db_create
   make db_load
   ```

2. Verify everything works:
   ```bash
   make ps              # All services running?
   make logs-mcp        # MCP server healthy?
   curl http://localhost:4000/api/players  # Flask responding?
   ```

3. Try connecting to Claude or Cursor (optional):
   - Follow the HTTP/SSE setup steps
   - See if tools appear
   - Ask a simple question

Don't worry if connection doesn't work yet - we'll debug everything together in Class 18!


