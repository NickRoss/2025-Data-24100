<!---
title: "MCP Continued"
--->

# MCP Continued

## Connecting MCP Server to Claude Desktop

- Claude Desktop is Anthropic's desktop application for Claude
- It supports MCP servers through configuration files
- Configuration location depends on your operating system

### Configuration File

- Create or edit the Claude Desktop configuration file
- Add your MCP server configuration:

```json
{
  "mcpServers": {
    "basketball-api": {
      "command": "docker",
      "args": [
        "compose",
        "run",
        "--rm",
        "mcp-server",
        "python",
        "/app/mcp_server/server.py"
      ]
    }
  }
}
```

- Restart Claude Desktop after configuration changes
- Claude Desktop will discover and connect to your MCP server

## Connecting MCP Server to Cursor

- Cursor is a code editor with built-in AI assistance
- It also supports MCP servers
- Configuration is done through Cursor's settings

### Cursor Configuration

- Open Cursor settings
- Navigate to MCP/Extensions settings
- Add your MCP server configuration
- Cursor will connect to your server and make tools available

## Interactive Usage

- Once connected, you can ask Claude or Cursor questions that trigger tool usage
- Example queries:
  - "Get me a list of all players"
  - "What colleges do players from WAS come from?"
  - "Create an account named 'Test User'"
  - "Calculate the return for account ID 1"

### How Tool Usage Works

1. **User asks a question** that requires external data or actions
2. **AI analyzes the question** and identifies which tools to use
3. **AI calls the tool(s)** with appropriate parameters
4. **Tool executes** and returns results
5. **AI incorporates results** into its response
6. **User sees the final answer** with tool results included

### Recognizing Tool Usage

- You can tell when tools are being used by:
  - Logs in your MCP server showing tool calls
  - Claude/Cursor indicating it's using tools
  - Responses that include data from your API/database

## Logging and Debugging

### MCP Server Logs

- MCP servers should log:
  - Server startup
  - Tool discovery requests
  - Tool execution calls
  - Tool execution results
  - Errors and exceptions

### Viewing Logs

- Use Docker Compose logs: `docker compose logs mcp-server`
- Follow logs in real-time: `docker compose logs -f mcp-server`
- Check for tool execution patterns

### Common Issues

- **Connection failures**: Check Docker network configuration
- **Tool not found**: Verify tool names match between definition and usage
- **Schema mismatches**: Ensure input schemas match what AI is sending
- **Timeout errors**: Check if Flask API is responding

## Real-World Patterns

### Exposing API Endpoints as Tools

- Each API endpoint can become an MCP tool
- Map REST endpoints to tool functions
- Handle authentication and error cases
- Return results in a format AI can understand

### Database Queries as Tools

- Expose database queries as tools
- Use parameterized queries for safety
- Return results as JSON
- Handle empty results gracefully

### Complex Operations

- Break complex operations into multiple tools
- Chain tools together when needed
- Provide clear descriptions for each tool
- Handle partial failures appropriately

## Best Practices

- **Tool Naming**: Use clear, descriptive names
- **Descriptions**: Write detailed descriptions that help AI understand when to use tools
- **Schemas**: Define proper input schemas using JSON Schema
- **Error Handling**: Return meaningful error messages
- **Logging**: Log all tool executions for debugging
- **Testing**: Test tools independently before connecting to AI assistants

## Final Project Requirements

- Your MCP server must expose at least 5 tools:
  - At least 2 from v1/v2 API endpoints
  - At least 2 from v3 API endpoints
  - At least 1 from v4 API endpoint (backtesting)
- Each tool must have proper schemas and error handling
- Server must be integrated into Docker Compose
- Must be connectable to Claude Desktop or Cursor
- Must include documentation on how to connect

## Summary

- MCP enables AI assistants to interact with your custom APIs and data
- MCP servers use async programming and HTTP streaming
- Tools expose your API functionality to AI assistants
- Proper logging and debugging are essential for MCP development
- The final project requires implementing a working MCP server

