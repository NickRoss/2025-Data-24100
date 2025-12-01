# Basketball API with MCP Server

This example demonstrates a complete implementation of a Flask API with an accompanying MCP (Model Context Protocol) server, both managed via Docker Compose.

## Architecture

This project consists of three services:

1. **Flask API** (`flask-app`): A RESTful API serving basketball data
2. **MCP Server** (`mcp-server`): An MCP server exposing the API functionality as tools for AI assistants
3. **Swagger UI** (`swagger-ui`): Interactive API documentation

All services communicate over a shared Docker network (`bball-network`).

## Prerequisites

- Docker and Docker Compose installed

## Quick Start

1. **Build and start Flask service:**
   ```bash
   make start-all
   ```
   Keep this running in the background.

2. **In a new terminal, create and load the database:**
   ```bash
   make db_create
   make db_load
   ```

3. **Access the services:**
   - Flask API: `http://localhost:4000`
   - Swagger UI: `http://localhost:8081`
   - API Documentation: `http://localhost:4000/docs`
   - MCP Server: `http://localhost:3000`

4. **Connect to your AI assistant** (see [Configuration](#connecting-mcp-server-to-ai-assistants))
   - The AI assistant will start the MCP server automatically when needed
   - Make sure Flask is still running (from step 1)

## Available Make Commands

### Service Management

- `make build` - Build all Docker images
- `make up` - Start all services in detached mode
- `make down` - Stop and remove all containers
- `make restart` - Restart all services
- `make ps` - Show running containers
- `make start-all` - Start Flask, MCP, and Swagger services
- `make stop-all` - Stop all services
- `make clean` - Remove all containers, networks, and volumes

### Flask Service

- `make flask` - Start Flask app only
- `make flask-dev` - Start Flask app in foreground with logs
- `make interactive` - Open bash shell in Flask container
- `make notebook` - Run Jupyter notebook server (port 8888)

### MCP Service

- `make mcp` - Start MCP server
- `make mcp-dev` - Start MCP server in foreground with logs
- `make mcp-test` - Test MCP server connection
- `make mcp-interactive` - Open bash shell in MCP server container

### Database Management

- `make db_create` - Create database schema
- `make db_load` - Load data into database
- `make db_rm` - Remove all data from database
- `make db_clean` - Clean the database
- `make db_interactive` - Open interactive SQLite shell

### Documentation & Testing

- `make autodoc` - Serve MkDocs documentation (port 4040)
- `make test` - Run pytest with coverage
- `make swagger` - Start Swagger UI only

### Logging

- `make logs` - Show logs from all services
- `make logs-flask` - Show logs from Flask app only
- `make logs-mcp` - Show logs from MCP server only
- `make logs-swagger` - Show logs from Swagger UI only

## MCP Server Tools

The MCP server exposes the following tools for AI assistants:

### 1. `get_all_players`
Get a list of all basketball players in the database, grouped by team.

**Parameters:** None

**Example use:** "Show me all players in the database"

### 2. `get_player_info`
Get detailed information about a specific player by their ID.

**Parameters:**
- `player_id` (integer, required): The unique ID of the player

**Example use:** "Get information about player ID 42"

### 3. `get_players_by_team`
Get all players for a specific team.

**Parameters:**
- `team` (string, required): The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')

**Example use:** "Show me all players on the Lakers" (uses 'LAL')

### 4. `add_player`
Add a new player to the database.

**Parameters:**
- `player_name` (string, required): The name of the player
- `team` (string, required): The 3-letter team abbreviation (e.g., 'LAL', 'WAS', 'BOS')
- `college` (string, optional): The college the player attended

**Example use:** "Add a new player named John Doe to the Boston Celtics from Duke" (uses 'BOS')

### 5. `delete_player`
Delete a player from the database by their ID.

**Parameters:**
- `player_id` (integer, required): The unique ID of the player to delete

**Example use:** "Delete player ID 42"

### 6. `get_players_by_college`
Get all players who attended a specific college.

**Parameters:**
- `college` (string, required): The college name

**Example use:** "Show me all players from Duke"

## Connecting MCP Server to AI Assistants

### Method 1: HTTP/SSE (Recommended - Simpler!) ⭐

This is the easiest way - just use a URL!

1. **Start all services:**
   ```bash
   make start-all
   ```
   Keep this running.

2. **Add to your AI assistant config:**

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

**Cursor** (`~/.cursor/mcp.json` or `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`):
```json
{
  "mcpServers": {
    "basketball-api": {
      "url": "http://localhost:3000/sse",
      "description": "Basketball API MCP Server (HTTP/SSE) - Query basketball player data"
    }
  }
}
```

3. **Restart your AI assistant**

**That's it!** The MCP server is already running at http://localhost:3000

### Method 2: Claude Desktop with mcp-remote

For Claude Desktop, you can also use the `mcp-remote` package:

1. **Install mcp-remote globally:**
   ```bash
   npm install -g mcp-remote
   ```

2. **Add to Claude Desktop config** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "basketball": {
         "command": "mcp-remote",
         "args": [
           "http://localhost:3000/sse"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### Method 3: stdio (On-Demand)

Alternatively, let the AI assistant start the MCP server on-demand:

**Claude Desktop / Cursor:**
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

With this method, run `make flask` (keep it running), and the AI will start/stop MCP as needed.

**Recommended:** Use Method 1 for simplicity!

## Project Structure

```
17_MCP/
├── docker-compose.yml      # Service orchestration
├── Makefile                # Convenience commands
├── README.md               # This file
├── flask_app/              # Flask application
│   ├── Dockerfile
│   ├── flask_app.py
│   ├── pyproject.toml
│   ├── app/                # Application code
│   │   ├── api/           # API routes
│   │   ├── data_utils/    # Database utilities
│   │   ├── logger_utils/  # Logging configuration
│   │   └── route_utils/   # Route decorators
│   ├── data/              # Database and CSV files
│   └── api-docs/          # MkDocs documentation
└── mcp_server/            # MCP server
    ├── Dockerfile
    ├── server.py          # MCP server implementation
    ├── tools.py           # MCP tool definitions
    └── pyproject.toml     # Dependencies
```

## How It Works

### Communication Flow

1. **AI Assistant → MCP Server**: AI assistants communicate with the MCP server using the MCP protocol (via stdio)
2. **MCP Server → Flask API**: The MCP server makes HTTP requests to the Flask API
3. **Flask API → Database**: The Flask API queries the SQLite database
4. **Response Flow**: Data flows back through the same chain

### Why Docker Compose?

Docker Compose allows us to:
- Manage multiple services (Flask, MCP, Swagger) together
- Share a Docker network for inter-service communication
- Use service names as hostnames (e.g., `http://flask-app:5000`)
- Start/stop all services with a single command
- Ensure proper startup order with `depends_on` and health checks

### MCP Server Implementation Details

The MCP server (`mcp_server/server.py`) uses:
- **`FastMCP`**: FastMCP framework for building MCP servers
- **`httpx`**: Async HTTP client for making requests to Flask API
- **HTTP/SSE transport**: Server-Sent Events for real-time communication

The server is implemented using FastMCP, which simplifies tool definition and transport handling. Tools are defined in `mcp_server/tools.py` and registered with the FastMCP instance.

Each tool:
1. Defines a clear name and description
2. Makes HTTP requests to the Flask API
3. Returns formatted responses to the AI assistant

**Note:** Team parameters use 3-letter abbreviations (e.g., 'LAL' for Los Angeles Lakers, 'WAS' for Washington Wizards, 'BOS' for Boston Celtics).

## Development Workflow

1. **Start the Flask API:**
   ```bash
   make flask-dev
   ```

2. **In another terminal, test the API:**
   ```bash
   curl http://localhost:4000/api/players
   ```

3. **Test the MCP server:**
   ```bash
   make mcp-test
   ```

4. **View logs:**
   ```bash
   make logs-flask  # Flask logs
   make logs-mcp    # MCP logs
   ```

## Troubleshooting

### MCP server can't connect to Flask API

Make sure Flask is running and healthy:
```bash
make ps  # Check if flask-app is running
make logs-flask  # Check Flask logs
```

### Database not found

Create and load the database:
```bash
make db_create
make db_load
```

### Port conflicts

If ports 4000, 8080, or 8888 are in use, stop other services or modify the ports in `docker-compose.yml`.

### MCP tools not appearing in AI assistant

1. Check that the MCP server starts without errors: `make mcp-dev`
2. Verify your MCP configuration file path is correct
3. Restart your AI assistant after updating the configuration

## Example Usage with Claude/Cursor

Once connected, you can ask questions like:

- "Show me all basketball players in the database"
- "Get information about player ID 5"
- "List all players from the Lakers" (uses 'LAL')
- "Get all players from the Wizards" (uses 'WAS')
- "Add a new player named Michael Jordan to the Chicago Bulls from UNC" (uses 'CHI')
- "Show me all players who went to Duke"
- "What college did Kyle Kuzma go to?"

The AI assistant will automatically use the appropriate MCP tools to fetch and display the data. Remember that team names should be provided as 3-letter abbreviations (e.g., 'LAL', 'WAS', 'BOS', 'CHI').

## Further Reading

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
