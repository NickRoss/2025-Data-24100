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

- Understand why Docker Compose is used for managing multiple services
- Be able to read and interpret: port and volume settings in a docker compose file. Why are they required?
- Know how to use Docker networks for inter-service communication
- Understand how to view logs
- Know how services use service names as hostnames
- Recognize the difference between internal service communication and external access

### MCP Server Implementation with FastMCP

- Why is async required?
- What is a tool?

### Tool Design and Registration

- Understand how to write clear docstrings for MCP tools
- Understand how FastMCP extracts tool metadata from functions
- Recognize the importance of type hints and docstring structure
- Know how the AI interprets tool descriptions
- Understand why TypedDict is used for structured response types in MCP tools (direct JSON compatibility)

