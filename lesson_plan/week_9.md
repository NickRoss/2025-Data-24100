# Week #9 Lesson Plan

## Overview

- There is no quiz this week.
- Next week the [final part](../project_assignments/part_7.md) of the project and the [final exam](./finals_week.md) will occur.
- This week we dive deep into MCP implementation and practical usage.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/use-mcp-with-claude-desktop)
- [Cursor MCP Integration](https://cursor.com/docs/context/mcp)
- [httpx Documentation](https://www.python-httpx.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- Lecture example: `lecture_examples/17_MCP`

## Lecture notes

- [Day 17 (MCP Implementation)](../class_notes/17_mcp_implementation.md)
- [Day 18 (MCP Continued)](../class_notes/18_mcp_continued.md)

## Learning Objectives / Quizzable Concepts

### Docker Compose for Multi-Service Systems

- Understand why Docker Compose is used for managing **multiple coordinated services** (Flask API, MCP server, Swagger UI)
- Be able to read and interpret key parts of a `docker-compose.yml` file:
  - **Services**, **build context**, and **Dockerfiles**
  - **Port mappings** (host vs container ports) and why they matter
  - **Volume mounts** and how they enable live code changes
  - **Environment variables** such as `FLASK_API_URL`, `DB_PATH`, and `DATA_DIR`
  - **Networks** and `depends_on`
- Use `docker ps` and `docker compose logs` output to verify that services are running and to debug issues


### MCP Server Architecture with FastMCP

- Understand the overall **project structure** for the basketball example:
  - `flask_app/` (Flask API)
  - `mcp_server/` (FastMCP-based MCP server)
- Explain the role of **FastMCP** and the `mcp` instance:
  - `server.py` imports `mcp` from `tools.py` and starts the MCP server
  - Tools are defined and registered in `tools.py` using decorators

### Async Programming and httpx

- Explain what async is and why we use it.
- Explain specifically why MCP tools are written as **async functions** (`async def`) instead of synchronous functions.

### Tool Design, Types, and Registration

- Define what a **tool** is in MCP: a function exposed for AI assistants to call
- Understand how FastMCP turns a Python function into a tool:
  - Uses the function name as the tool name
  - Uses the docstring as the description
  - Parses an `Args:` section and type hints to build the parameter schema
- Recognize the importance of:
  - Clear **docstrings** that describe purpose, arguments, and return values
  - **Type hints** on parameters and return types
- Understand why we use **type aliases** for responses (e.g., `PlayerDict`, `PlayerInfo`, `AllPlayersResponse`) instead of raw `dict[str, Any]` everywhere:
  - Improved readability
  - Better JSON Schema generation in FastMCP
  - Direct compatibility with `response.json()` output
- Compare returning:
  - A **stringified** JSON result (`str(response.json())`)
  - A **typed dictionary** result (e.g., `AllPlayersResponse`) and how each affects what the AI sees


