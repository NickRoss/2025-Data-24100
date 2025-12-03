<!---
title: "MCP Continued: Connecting to AI Assistants"
--->

# MCP Continued: Connecting to AI Assistants

## Recap from Class 17

We built a multi-service system with:
- **Flask API** - serving basketball data
- **MCP Server** - exposing API functionality as tools
- **Swagger UI** - API documentation

In Lecture 17, we saw that MCP tools use `async def` and `httpx` to make HTTP requests, but we didn't explain how these work. Today we'll:
1. **Understand httpx and async programming** - Learn how tools make HTTP requests
2. **Connect the MCP server to AI assistants** - See the complete workflow in action
3. **Test and debug** - Monitor tool execution and troubleshoot issues

## Understanding httpx

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

Breaking it down:

- `async with httpx.AsyncClient() as client:` - Creates HTTP client, closes when done
- `await client.get(...)` - Makes HTTP GET request, waits for response
- `response.raise_for_status()` - Throws error if request failed
- `response.json()` - Parses JSON response body
- `str(result)` - Converts to string for AI to read


## Async Programming Basics

**What problem does async solve?**

Synchronous (blocking) code:
```python
def process_requests():
    data1 = call_api()        # Wait 2 seconds
    result1 = process(data1)  # Wait 1 second
    data2 = call_api()        # Wait 2 seconds
    result2 = process(data2)  # Wait 1 second
    # Total time: 6 seconds
```

Asynchronous (non-blocking) code:
```python
async def process_requests():
    data1_task = asyncio.create_task(call_api())  # Start, don't wait
    data2_task = asyncio.create_task(call_api())  # Start, don't wait
    
    data1 = await data1_task  # Get result when ready
    data2 = await data2_task  # Get result when ready
    # Total time: ~2 seconds (both ran at same time!)
```

**Async keywords:**

- **`async def`** - Defines an async function (coroutine)
- **`await`** - Waits for an async operation to complete (can only use inside `async def` functions)
- **`async with`** - Async context manager

Example:
```python
async def my_function():
    return "result"

result = await my_function()  # Pause here until done

async with httpx.AsyncClient() as client:
    response = await client.get("http://example.com")
    # Client is automatically closed
```

**When to use async:**

Use async for:
- Making HTTP requests (like our MCP tools)
- Querying databases
- Reading/writing files
- Any I/O-bound operation

Don't use async for:
- CPU-bound operations (calculations, data processing)
- Simple scripts that only do one thing at a time

**Common async patterns:**

Pattern 1 - Making one request:
```python
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://api.example.com/data")
        return response.json()
```

Pattern 2 - Making multiple requests sequentially:
```python
async def get_player_and_team(player_id):
    async with httpx.AsyncClient() as client:
        player = await client.get(f"/api/players/{player_id}")
        team = await client.get(f"/api/teams/{player.json()['team']}")
        return player.json(), team.json()
```

Pattern 3 - Making multiple requests concurrently:
```python
async def get_multiple_players(player_ids):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(f"/api/players/{pid}") for pid in player_ids]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
```
## Connecting to AI Assistants

Once your MCP server is running via `make start-all`, you can connect it to AI assistants like Claude Desktop or Cursor using HTTP/SSE.

**Note:** Some AI assistants require HTTPS instead of HTTP. Our local setup uses HTTP, which works with Cursor and Claude Desktop (via mcp-remote). For production deployments, you would need HTTPS.

**Method 1: HTTP/SSE with Direct URL (Simplest)**

If your MCP server is running continuously (via `make start-all`), you can connect directly via URL.

Cursor configuration (`~/.cursor/mcp.json` in your home directory, _not_ project root):
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

**Method 2: HTTP/SSE with mcp-remote (Claude Desktop)**

`mcp-remote` is an npm package that wraps HTTP/SSE connections in a stdio interface for Claude Desktop. You will need to install this separately in order to use it.

Install mcp-remote:
```bash
npm install -g mcp-remote
```

Configure Claude Desktop. This file needs to go into Claude's configuration file. On my machine that can be found at: `~/Library/Application Support/Claude/claude_desktop_config.json`

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

**Cursor-specific verification:**

1. Start the services: `cd lecture_examples/17_MCP && make start-all`
2. Create/edit config file: `mkdir -p ~/.cursor && nano ~/.cursor/mcp.json`
3. Add configuration (see JSON above)
4. Restart Cursor completely (not just reload window)
5. Verify connection: Open a new chat and ask "What MCP tools do you have available?"

**Claude Desktop-specific verification**

1. Install MCP Remote (as above)
2. Edit/Create a configuration file (see above). Configuration file locations are:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  - Linux: `~/.config/Claude/claude_desktop_config.json`
3. Add the configuration information from above to the file
4. Make sure the services are started
5. Restart Claude Desktop after configuration


## Understanding Tool Schemas

Now that we understand httpx and async programming, let's look at a complete tool definition from `tools.py`:

```python
@mcp.tool()
async def get_players_by_team(team: str) -> str:
    """Get all players for a specific team.
    
    Args:
        team: The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')
    
    Returns a list of all players on that team.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FLASK_API_URL}/api/teams/players/{team}/list"
        )
        response.raise_for_status()
        return str(response.json())
```

**Breaking down the implementation:**
- `async def` - This is an async function (as we learned earlier)
- `async with httpx.AsyncClient() as client:` - Creates an HTTP client for making requests
- `await client.get(...)` - Makes an HTTP GET request and waits for the response
- `response.raise_for_status()` - Raises an exception if the HTTP request failed
- `str(response.json())` - Converts the JSON response to a string for the AI to read

**Note on return types:** This example returns `str`, but you can also return the JSON directly (like `AllPlayersResponse` in Lecture 17). FastMCP will handle both - returning a string is more explicit about what the AI receives, while returning a typed dict provides better type safety. Both approaches work fine.

**What FastMCP does automatically:**
- Extracts tool name from function name: `get_players_by_team`
- Uses docstring as description
- Infers parameter schema from type hints: `team: str`
- Extracts parameter descriptions from `Args:` section
- Returns string (AI interprets the data)

**The AI sees:**
```json
{
  "name": "get_players_by_team",
  "description": "Get all players for a specific team...",
  "parameters": {
    "type": "object",
    "properties": {
      "team": {
        "type": "string",
        "description": "The 3-letter team abbreviation..."
      }
    },
    "required": ["team"]
  }
}
```
