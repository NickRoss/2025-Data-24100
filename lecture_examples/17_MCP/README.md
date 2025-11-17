# Basketball API with MCP Server

This repository demonstrates a Flask API with an MCP (Model Context Protocol) server that exposes API functionality as tools for AI assistants.

## Project Structure

- `flask_app/` - Flask application code (based on `16_compose`)
- `mcp_server/` - MCP server implementation
- `pyproject.toml` - Python dependencies
- `docker-compose.yml` - Docker Compose configuration with Flask and MCP services
- `Makefile` - Convenient commands for common tasks

## Quick Start

### Build and run all services (Flask API + MCP Server):
```bash
make build
make up
```

The API will be available at `http://localhost:4000`
The MCP server will be available for connection via stdio or HTTP

### Run only the Flask API:
```bash
make flask
```

### Run only the MCP server:
```bash
make mcp
```

## MCP Server

The MCP server exposes API endpoints as tools that AI assistants can use. The server is based on the MCP Python SDK and uses async/await patterns.

### Connecting to MCP Clients

#### Claude Desktop
Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "basketball-api": {
      "command": "docker",
      "args": ["compose", "run", "--rm", "mcp-server", "python", "/app/mcp_server/server.py"]
    }
  }
}
```

#### Cursor
Configure in Cursor's MCP settings to connect to the MCP server.

## Available MCP Tools

The MCP server exposes the following tools:
- `get_player_list` - Get list of all players
- `get_players_by_team` - Get players for a specific team
- `get_colleges_by_team` - Get colleges for a specific team
- (Additional tools as implemented)

## Technologies

- Flask for the REST API
- MCP Python SDK for the MCP server
- Docker Compose for multi-container orchestration
- SQLite for data storage
- uv for Python package management

**NOTE** This is demonstration code for educational purposes.

