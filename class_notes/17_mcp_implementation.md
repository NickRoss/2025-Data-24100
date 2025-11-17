<!---
title: "MCP Implementation"
--->

# MCP Implementation

## MCP Server Structure

- An MCP server is typically a separate service in your Docker Compose setup
- It uses the MCP Python SDK to expose tools, resources, and prompts
- The server communicates with MCP clients via stdio or HTTP

## Setting Up an MCP Server

### Installation

- Install the MCP Python SDK: `uv add mcp`
- The MCP SDK provides the framework for building MCP servers

### Basic MCP Server Structure

```python
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create the server
server = Server("my-api-server")

# Define tools
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_player_list",
            description="Get a list of all players in the database",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # More tools...
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_player_list":
        # Call your Flask API or database
        result = await fetch_players()
        return [TextContent(type="text", text=result)]
    # Handle other tools...
```

## Async Programming

- MCP servers use async/await patterns instead of synchronous code
- **Why async?**
  - Allows handling multiple requests concurrently
  - Enables streaming responses
  - More efficient for I/O-bound operations (API calls, database queries)

### Async vs Sync

- **Synchronous (Flask)**: One request at a time, blocking
  ```python
  def get_players():
      result = database.query("SELECT * FROM players")
      return result
  ```

- **Asynchronous (MCP)**: Multiple requests concurrently, non-blocking
  ```python
  async def get_players():
      result = await database.query("SELECT * FROM players")
      return result
  ```

### Basic Async Concepts

- `async def` - Defines an async function
- `await` - Waits for an async operation to complete
- `asyncio.run()` - Runs an async function
- Async functions can call other async functions with `await`

## HTTP Streaming and Server-Sent Events (SSE)

- MCP uses HTTP streaming for real-time communication
- **Server-Sent Events (SSE)** allow servers to push data to clients over HTTP
- Unlike REST (request → wait → response), SSE enables:
  - Real-time updates
  - Streaming responses
  - Long-lived connections

### Why Not REST?

- REST is request-response: one request, one response, connection closes
- MCP needs:
  - Streaming tool execution results
  - Real-time feedback during long operations
  - Continuous communication between client and server
- SSE provides the streaming capability that REST lacks

## Exposing Flask API Endpoints as MCP Tools

- Your MCP server can call your Flask API endpoints
- Two approaches:
  1. **HTTP requests**: MCP server makes HTTP requests to Flask API
  2. **Shared code**: MCP server imports and calls Flask API functions directly

### HTTP Request Approach

```python
import httpx

async def get_players():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://flask-app:5000/api/players")
        return response.json()
```

### Shared Code Approach

```python
from flask_app import create_app
from app.data_utils import get_all_players

async def get_players():
    # Use shared database functions
    players = await get_all_players()
    return players
```

## Tool Definition Best Practices

- **Clear names**: Use descriptive, action-oriented names
  - Good: `get_player_list`, `create_account`, `calculate_return`
  - Bad: `player`, `data`, `stuff`
- **Detailed descriptions**: Explain what the tool does and when to use it
- **Proper schemas**: Use JSON Schema to define input parameters
- **Error handling**: Handle errors gracefully and return meaningful messages

## Docker Compose Integration

- Add MCP server as a service in `docker-compose.yml`:

```yaml
services:
  flask-app:
    # ... Flask service definition

  mcp-server:
    build:
      context: .
      dockerfile: mcp_server/Dockerfile
    container_name: my_mcp_server
    depends_on:
      - flask-app
    networks:
      - app-network
    # MCP server configuration
```

- The MCP server can communicate with Flask API via the Docker network
- Use service names as hostnames: `http://flask-app:5000`

## Testing MCP Servers

- Test MCP servers locally before connecting to AI assistants
- Use the MCP SDK's testing utilities
- Verify tool discovery and execution
- Check error handling

## Next Steps

- In the next lecture, we'll connect the MCP server to Claude Desktop and Cursor
- We'll see how AI assistants use the tools
- We'll debug and monitor MCP server activity

