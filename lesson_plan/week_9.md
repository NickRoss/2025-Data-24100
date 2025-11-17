# Week #9 Lesson Plan

## Overview

- [Part 7](../project_assignments/part_7.md) of the project is due Wednesday at midnight.
- There is no quiz this week.
- Next week the [final part](../project_assignments/part_8.md) of the project and the [final exam](./finals_week.md) will occur.
- This week we dive deep into MCP implementation and practical usage.

## Resources

- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/use-mcp-with-claude-desktop)
- [Cursor MCP Integration](https://cursor.sh/docs/mcp)
- Lecture example: `lecture_examples/17_MCP`

## Learning Objectives

### MCP Server Implementation

- Understand the structure of an MCP server
- Know how to create an MCP server using the Python SDK
- Understand how to define tools that expose your API functionality
- Understand how to expose resources (data sources)
- Know how to handle tool execution and return results

### Async Programming

- Understand why MCP uses async/await patterns
- Recognize the difference between synchronous Flask and asynchronous MCP servers
- Understand how async enables concurrent handling of multiple requests
- Understand basic async/await syntax in Python
- Recognize when to use async vs sync code

### HTTP Streaming and SSE

- Understand Server-Sent Events (SSE) and how they differ from REST
- Understand why streaming is important for AI agent interactions
- Recognize how MCP uses streaming for real-time tool execution feedback
- Understand the difference between request-response (REST) and streaming (SSE) patterns

### MCP Server Architecture

- Understand how to structure an MCP server project
- Know how to integrate an MCP server with existing Flask APIs
- Understand how to expose database queries as MCP tools
- Recognize best practices for tool design (clear names, good descriptions, proper schemas)

### Practical Usage

- Understand how to test an MCP server locally
- Know how to connect an MCP server to Claude Desktop or Cursor
- Understand how to debug MCP server issues using logs
- Recognize common patterns for exposing API endpoints as MCP tools

### MCP Client Configuration

- Understand how to configure Claude Desktop to connect to an MCP server
- Understand how to configure Cursor to use MCP servers
- Know how to set up MCP server connections in client configuration files
- Understand authentication and security considerations

### Interactive MCP Usage

- Understand how to ask questions that trigger MCP tool usage
- Recognize when an AI assistant is using MCP tools vs. generating responses directly
- Understand how tool results are incorporated into AI responses
- Know how to verify that tools are being called correctly

### Logging and Debugging

- Understand how to read MCP server logs
- Recognize log patterns that indicate tool execution
- Understand how to debug MCP connection issues
- Know how to verify that tools are being discovered correctly

## Lecture notes

- [Day 17 (MCP Implementation)](../class_notes/17_mcp_implementation.md)
- [Day 18 (MCP Continued)](../class_notes/18_mcp_continued.md)

## Quizzable Concepts

### MCP Server Implementation

- How do you define a tool in an MCP server?
- What information should be included in a tool definition (name, description, input schema)?
- How does an MCP server handle tool execution requests?

### Async Programming

- Why does MCP use async/await instead of synchronous code?
- What is the difference between `async def` and regular `def` functions?
- How do you call an async function from another async function?
- What is the difference between Flask (sync) and MCP (async) request handling?

### HTTP Streaming

- What is Server-Sent Events (SSE)?
- How does SSE differ from traditional REST API request-response patterns?
- Why is streaming important for AI agent interactions?
- Why can't we use REST APIs for MCP? (Hint: streaming, real-time feedback)

### MCP Architecture

- How do you structure an MCP server to work alongside a Flask API?
- What is the relationship between your Flask API endpoints and MCP tools?
- How do you expose database queries as MCP tools?
- What makes a good tool definition? (clear purpose, good description, proper schema)

### MCP Client Configuration

- How do you configure Claude Desktop to connect to an MCP server?
- What information is needed in an MCP client configuration file?
- How do you verify that an MCP server is connected correctly?

### Interactive Usage

- How can you tell when an AI assistant is using an MCP tool?
- What happens when an MCP tool is called?
- How are tool results incorporated into AI responses?

### Logging and Debugging

- What should you look for in MCP server logs to verify it's working?
- How do you debug MCP connection issues?
- What log patterns indicate successful tool execution?

### MCP Patterns

- What makes a good MCP tool definition?
- How do you expose a Flask API endpoint as an MCP tool?
- How do you expose database queries as MCP tools?
- What are common error patterns in MCP implementations?