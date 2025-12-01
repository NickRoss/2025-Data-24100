<!---
title: "MCP Continued: Connecting to AI Assistants"
--->

# MCP Continued: Connecting to AI Assistants

## Recap from Class 17

We built a multi-service system with:
- **Flask API** - serving basketball data
- **MCP Server** - exposing API functionality as tools
- **Swagger UI** - API documentation

Today we'll connect the MCP server to AI assistants and see the complete workflow in action.

## Understanding MCP Transport Modes

The MCP server can run in two different modes:

### 1. stdio (Standard Input/Output)

```python
# server.py runs in stdio mode by default
mcp.run()  # No arguments = stdio
```

**How it works:**
- AI assistant **starts the MCP server** when needed
- Communication happens via stdin/stdout (like piping in shell)
- Server **shuts down** when AI disconnects
- No network ports needed

**When to use:**
- Running server on-demand
- Single user scenarios
- Simpler configuration

### 2. HTTP/SSE (Server-Sent Events)

```python
# server.py with --http flag
mcp.run(transport="sse", host="0.0.0.0", port=3000)
```

**How it works:**
- MCP server **runs continuously** on a port (like Flask)
- AI assistant **connects via HTTP** to the URL
- Uses Server-Sent Events for streaming
- Multiple clients can connect

**When to use:**
- Server should stay running
- Multiple users/assistants
- Easier to debug (can see logs continuously)

## Connecting to Claude Desktop

### Method 1: HTTP/SSE (Recommended - Easier to Debug!)

**Step 1: Start the system**

```bash
cd lecture_examples/17_MCP
make start-all
```

This starts Flask, MCP server (in HTTP mode), and Swagger UI.

**Step 2: Verify MCP is running**

```bash
make ps
# Should show: bball_mcp_server running on port 3000
```

**Step 3: Create/load database**

```bash
make db_create
make db_load
```

**Step 4: Configure Claude Desktop**

Find the configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Create or edit the file:

```json
{
  "mcpServers": {
    "basketball-api": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

**Key points:**
- `basketball-api` is a name you choose (can be anything)
- `url` points to the MCP server's SSE endpoint
- The path `/sse` is defined in the MCP server code

**Step 5: Restart Claude Desktop**

Completely quit and restart Claude Desktop.

**Step 6: Verify connection**

Open Claude Desktop and check for the MCP tool icon or look for "basketball-api" in available tools.

### Method 2: stdio with Docker

This method lets Claude Desktop start/stop the MCP server on-demand.

**Configuration:**

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

**Important:**
- Must use **absolute path** to `docker-compose.yml`
- Flask must be running first: `make flask`
- Claude starts MCP when needed, stops when done

**Pros:**
- Server only runs when needed
- Automatic startup/shutdown

**Cons:**
- Harder to debug (server starts/stops quickly)
- Need Flask running already
- More complex path configuration

### Method 3: mcp-remote (Alternative for Claude Desktop)

If you prefer a simpler stdio-like approach:

**Install mcp-remote globally:**

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

This wraps the HTTP connection in an stdio interface.

## Connecting to Cursor

Cursor configuration is similar but uses a different file location.

### Method 1: HTTP/SSE (Simplest)

**Find Cursor's MCP config file:**
- `~/.cursor/mcp.json` 
- OR `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`

**Create/edit the file:**

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

**Start services:**

```bash
make start-all
make db_create
make db_load
```

**Restart Cursor**

### Method 2: stdio with Docker

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

Remember: Flask must be running first (`make flask` in background).

## Testing the Connection

### Verify MCP Tools are Available

**In Claude Desktop or Cursor, try asking:**

> "What MCP tools do you have available?"

You should see:
- `get_all_players`
- `get_player_info`
- `get_players_by_team`
- `add_player`
- `delete_player`
- `get_players_by_college`

### Test Basic Queries

**Start simple:**

> "Show me all basketball players in the database"

AI should use `get_all_players` tool.

**Test with parameters:**

> "Get information about player ID 5"

AI should use `get_player_info` with `player_id=5`.

**Test team queries:**

> "List all players on the Washington Wizards"

AI should use `get_players_by_team` with `team="WAS"` (3-letter abbreviation).

**Test college queries:**

> "Show me all players who went to Duke"

AI should use `get_players_by_college` with `college="Duke"`.

## Monitoring Tool Execution

### Viewing MCP Logs in Real-Time

**Terminal 1: Watch MCP logs**
```bash
make logs-mcp
```

**Terminal 2: Ask Claude/Cursor questions**

As you interact with the AI, you'll see logs like:

```
bball_mcp_server | INFO: Tool called: get_all_players
bball_mcp_server | INFO: Making request to http://flask-app:5000/api/players
bball_mcp_server | INFO: Tool execution successful
```

### Viewing Flask Logs

**Terminal 3: Watch Flask logs**
```bash
make logs-flask
```

You'll see:
```
bball_flask_app | INFO: GET /api/players - 200
bball_flask_app | INFO: Returned 25 players
```

### Understanding the Flow

1. **User asks Claude/Cursor:** "Show me all players"
2. **AI decides:** Need to call `get_all_players` tool
3. **MCP server receives:** Tool call request
4. **MCP logs:** "Tool called: get_all_players"
5. **MCP makes HTTP request:** To Flask API
6. **Flask logs:** "GET /api/players - 200"
7. **Flask returns data:** To MCP server
8. **MCP returns to AI:** Formatted response
9. **AI shows user:** Processed answer with data

## Debugging Common Issues

### Issue 1: MCP Tools Not Appearing

**Symptoms:**
- AI says "I don't have access to those tools"
- No MCP tools listed

**Checks:**

1. **Is MCP server running?**
   ```bash
   make ps | grep mcp
   ```

2. **Check MCP logs for errors:**
   ```bash
   make logs-mcp
   ```

3. **Verify config file location:**
   ```bash
   # macOS Claude Desktop:
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Cursor:
   cat ~/.cursor/mcp.json
   ```

4. **Restart AI assistant completely**

### Issue 2: Tool Execution Fails

**Symptoms:**
- AI says "Tool execution failed"
- MCP logs show errors

**Checks:**

1. **Is Flask running and healthy?**
   ```bash
   docker compose ps
   curl http://localhost:4000/api/players
   ```

2. **Check Flask logs:**
   ```bash
   make logs-flask
   ```
   Look for 500 errors or exceptions.

3. **Check database exists:**
   ```bash
   make db_interactive
   # Inside sqlite: .tables
   # Should show: players, team, stats
   ```

4. **Test Flask API directly:**
   ```bash
   curl http://localhost:4000/api/players
   curl http://localhost:4000/api/players/1
   ```

### Issue 3: Connection Refused

**Symptoms:**
- MCP logs show "Connection refused" to Flask
- Tools fail silently

**Diagnosis:**

```bash
# Check both services running
make ps

# Check if they're on the same network
docker network inspect bball-network
```

**Solutions:**

1. **Make sure Flask started first:**
   ```bash
   docker compose up -d flask-app
   # Wait a few seconds
   docker compose up -d mcp-server
   ```

2. **Check health status:**
   ```bash
   docker compose ps
   # flask-app should show "healthy"
   ```

3. **Restart in correct order:**
   ```bash
   make stop-all
   make start-all
   ```

### Issue 4: stdio Mode Doesn't Work

**Symptoms:**
- Server starts but immediately exits
- No tools appear in AI

**Common cause:** Flask isn't running.

**Solution:**

```bash
# Start Flask first, keep it running
make flask-dev

# In another terminal, try again in AI
```

For stdio mode, Flask must be running **before** AI starts MCP server.

## Advanced Usage Patterns

### Chaining Multiple Tools

AI can use multiple tools together:

**User:** "Add a new player named Test Player to the Wizards from Duke, then show me all Wizards players"

**AI will:**
1. Call `add_player(player_name="Test Player", team="WAS", college="Duke")`
2. Call `get_players_by_team(team="WAS")`
3. Show combined results

### Complex Queries

**User:** "How many players in the database went to Duke?"

**AI will:**
1. Call `get_players_by_college(college="Duke")`
2. Count the results
3. Return the number

### CRUD Operations

**Create:**
> "Add Michael Jordan to the Bulls from UNC"

**Read:**
> "Show me player ID 15"

**Update:**
(Note: Our API might not have update endpoint - AI will tell you this)

**Delete:**
> "Delete player ID 100"

## Development Workflow Tips

### Best Setup for Development

**Terminal 1: Flask (foreground)**
```bash
make flask-dev
```
See Flask logs immediately.

**Terminal 2: MCP (foreground)**
```bash
make mcp-dev
```
See MCP logs immediately.

**Terminal 3: Database operations**
```bash
make db_create
make db_load
```

**Terminal 4: Manual testing**
```bash
curl http://localhost:4000/api/players
```

### Production-Like Setup

Use background services:

```bash
make start-all    # All services detached
make logs         # View all logs together
```

Switch between services:
```bash
make logs-flask   # Focus on Flask
make logs-mcp     # Focus on MCP
```

## Understanding Tool Schemas

Let's look at a tool definition from `tools.py`:

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

## Clean Shutdown

Always clean up properly:

**Stop all services:**
```bash
make stop-all
```

**Or if you want to clean everything (including volumes):**
```bash
make clean
```

**Check nothing is running:**
```bash
docker ps
```

## Key Takeaways

1. **Two transport modes:** stdio (on-demand) vs HTTP/SSE (persistent)
2. **HTTP/SSE is easier to debug** - logs are visible continuously
3. **stdio requires Flask running first** - dependency must be managed
4. **Monitor logs** to understand tool execution flow
5. **Services must be healthy** before MCP can connect
6. **AI interprets tool descriptions** - write clear docstrings
7. **Network matters** - services communicate via Docker network names
8. **Configuration paths** - must be absolute for stdio mode

## Practice Exercises

1. **Start the system and connect to Claude/Cursor**
   - Verify all tools appear
   - Try each tool with a test query

2. **Monitor a complete interaction**
   - Watch logs in one terminal
   - Ask AI questions in another
   - Observe the full request/response cycle

3. **Intentionally break something**
   - Stop Flask while MCP is running
   - See what error messages appear
   - Fix it and verify recovery

4. **Switch transport modes**
   - Try HTTP/SSE method
   - Try stdio method
   - Compare ease of debugging

5. **Test error handling**
   - Request invalid player ID
   - Query non-existent team
   - See how errors are reported to AI

## Next: Final Project

For your final project (Part 7), you'll build a similar MCP server for your stock trading API:

**Required tools:**
- At least 5 tools exposing your API functionality
- Mix of v1, v2, v3, and v4 endpoints
- Proper error handling
- Clear documentation
- Working connection to Claude or Cursor

**Start planning:**
- Which endpoints to expose as tools?
- What parameters do they need?
- How will you describe them to AI?
- What error cases need handling?

The basketball API example is a complete template - adapt it for your stock API!
