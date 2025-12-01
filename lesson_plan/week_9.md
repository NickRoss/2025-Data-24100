# Week #9 Lesson Plan

## Overview

- There is no quiz this week.
- Next week the [final part](../project_assignments/part_7.md) of the project and the [final exam](./finals_week.md) will occur.
- This week we dive deep into MCP implementation and practical usage.

## Resources

`- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/use-mcp-with-claude-desktop)
- [Cursor MCP Integration](https://cursor.com/docs/context/mcp)
- [httpx Documentation](https://www.python-httpx.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- Lecture example: `lecture_examples/17_MCP`

## Learning Objectives

### Docker Compose for Multi-Service Systems

- Understand why Docker Compose is used for managing multiple services
- Know how to define services in `docker-compose.yml`
- Understand service dependencies and startup order
- Know how to use Docker networks for inter-service communication
- Understand volume mounts for development vs production
- Know how to start/stop services individually or together
- Understand how to view logs from multiple services

### MCP Server Implementation with FastMCP

- Understand the structure of an MCP server using FastMCP
- Know how to create async tool functions
- Understand how to register tools with the MCP server
- Understand how FastMCP reads docstrings to create tool definitions
- Know how to use type hints for parameter validation
- Understand the two transport modes: stdio and HTTP/SSE

### Async Programming Basics

- Understand why MCP uses async/await patterns (not on test but useful)
- Recognize the difference between synchronous Flask and asynchronous MCP servers
- Understand basic async/await syntax (`async def`, `await`)
- Know what httpx is and why it's used instead of requests
- Understand `async with` context managers

### HTTP Client with httpx

- Understand what httpx is (async HTTP client)
- Know how to make GET, POST, and DELETE requests with httpx
- Understand `async with httpx.AsyncClient()` pattern
- Know how to handle JSON responses
- Understand error handling with `raise_for_status()`

### Tool Design and Registration

- Understand how to write clear docstrings for MCP tools
- Know how the `register_tools()` function works
- Understand how FastMCP extracts tool metadata from functions
- Recognize the importance of type hints and docstring structure
- Know how the AI interprets tool descriptions

### MCP Server Architecture

- Understand how MCP server and Flask API communicate via Docker network
- Know how services use service names as hostnames
- Understand environment variables for configuration
- Recognize the difference between internal service communication and external access
- Know how to structure tool functions to call Flask API endpoints

### Practical Usage and Testing

- Know how to start the multi-service system with `make start-all`
- Understand how to view logs from individual services
- Know how to connect MCP server to Claude Desktop or Cursor
- Understand the difference between HTTP/SSE and stdio transports
- Know how to verify tools are available in AI assistants

### Logging and Debugging Multi-Service Systems

- Understand how to read logs from multiple services
- Know how to use `docker compose logs` with service filters
- Understand how to debug service connectivity issues
- Recognize common error patterns (connection refused, port conflicts)
- Know how to verify services are running with `docker compose ps`

## Lecture notes

- [Day 17 (MCP Implementation)](../class_notes/17_mcp_implementation.md)
- [Day 18 (MCP Continued)](../class_notes/18_mcp_continued.md)

## Quizzable Concepts

### Docker Compose Multi-Service Systems

- How do services communicate with each other in Docker Compose?
- What is the difference between service names and localhost?
- How do you view logs from a specific service?
- What is the difference between `ports` and internal service communication?
- How does `depends_on` work in docker-compose.yml?
- What command starts all services in detached mode?

### MCP Server with FastMCP

- How do you define a tool function for FastMCP?
- What is the `register_tools()` function and how does it work?
- How does FastMCP extract tool metadata from functions?
- What are the two transport modes for MCP servers?
- How do you specify that a function should be async?

### Tool Design and Docstrings

- Why are docstrings important in MCP tool definitions?
- What information does FastMCP extract from docstrings?
- How do type hints help with tool definitions?
- What makes a good tool description?
- How does the AI use tool descriptions?

### httpx HTTP Client

- What is httpx and why is it used instead of requests?
- How do you make a GET request with httpx?
- What does `async with httpx.AsyncClient()` do?
- What does `response.raise_for_status()` do?
- How do you make a POST request with JSON data?

### Service Communication

- How does the MCP server know the Flask API URL?
- What is `FLASK_API_URL` set to in the MCP container?
- Why use `http://flask-app:5000` instead of `http://localhost:5000`?
- How do Docker networks enable service discovery?
- What port does the host machine use to access Flask vs what port does MCP use?

### MCP Client Configuration

- What are the two methods to connect to an MCP server (HTTP/SSE vs stdio)?
- Where is Claude Desktop's MCP configuration file located?
- What information is needed in the configuration (url or command)?
- Why is HTTP/SSE easier to debug than stdio?
- What command shows running Docker containers?

### Logging and Debugging

- How do you view logs from only the MCP server?
- How do you view logs from all services at once?
- What does "connection refused" mean in MCP logs?
- How do you check if all services are running?
- What is the difference between `make logs` and `make logs-flask`?

### Volume Mounts and Development

- Why does the MCP server have a volume mount?
- What is the benefit of volume mounts for development?
- Do you need to rebuild the image when you change Python code with a volume mount?
- When DO you need to rebuild (dependencies vs code changes)?

### Commands and Makefile

- What does `make start-all` do?
- What does `make logs-mcp` do?
- How do you stop all services?
- What is the difference between `make flask` and `make start-all`?
- How do you create the database in a Docker Compose environment?