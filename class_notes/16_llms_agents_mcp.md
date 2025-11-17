<!---
title: "LLMs, Agents, and MCP"
--->

# LLMs, Agents, and MCP

## Large Language Models (LLMs)

- Large Language Models are AI systems trained on vast amounts of text data.
- They can generate human-like text, answer questions, and perform various language tasks.
- Examples: GPT-4, Claude, Gemini, Llama
- LLMs are powerful but have limitations:
  - They only know what they were trained on (knowledge cutoff date)
  - They can't directly interact with external systems
  - They can't perform actions in the real world

## AI Agents

- An AI Agent is an LLM that can use tools to interact with the outside world.
- Agents follow a loop: observe → think → act → observe
- **Observe**: Receive input (user query, tool results, system state)
- **Think**: Process information and decide what to do next
- **Act**: Execute actions (call tools, generate responses)
- **Observe**: See the results and continue the loop

### Tools in Agentic Systems

- Tools are functions that agents can call to interact with external systems.
- Examples of tools:
  - API calls to your Flask application
  - Database queries
  - File system operations
  - Web searches
  - Code execution
- Tools allow agents to go beyond their training data and interact with real systems.

## Model Context Protocol (MCP)

- MCP is a protocol that enables AI assistants to securely connect to external tools and data sources.
- It provides a standardized way for AI assistants to discover and use capabilities from external systems.
- MCP was created by Anthropic to enable Claude and other AI assistants to interact with custom APIs and data.

### MCP Architecture

- **MCP Server**: Exposes capabilities (tools, resources, prompts) to AI assistants
- **MCP Client**: AI assistant (like Claude Desktop, Cursor) that connects to servers
- **Protocol**: Standardized communication format between client and server

### Key MCP Concepts

- **Tools**: Functions that an AI can call to interact with external systems
  - Each tool has a name, description, and input schema
  - Tools can perform actions (query databases, call APIs, etc.)
- **Resources**: Data sources that an AI can read
  - Files, database tables, API endpoints
  - Resources provide context without performing actions
- **Prompts**: Pre-defined prompt templates
  - Reusable prompts for common tasks
- **Sampling**: Streaming responses from tools
  - Allows real-time feedback during tool execution

### Why MCP vs REST?

- **HTTP Streaming**: MCP uses Server-Sent Events (SSE) for real-time communication
  - REST APIs are request-response based (one request, one response)
  - MCP supports streaming, allowing incremental updates and real-time feedback
- **AI-Optimized**: MCP is designed specifically for AI agent interactions
  - Structured schemas that AI can understand
  - Tool discovery and introspection
  - Built-in support for streaming and async operations
- **Protocol vs API**: MCP is a protocol, not just an API
  - Standardized way to expose capabilities
  - Works across different AI assistants (Claude, Cursor, etc.)
  - Enables tool composition and chaining

### MCP Use Cases

- Exposing your Flask API as tools that AI assistants can use
- Providing database access to AI assistants
- Enabling AI assistants to interact with your custom data sources
- Creating domain-specific AI capabilities (e.g., stock market analysis, scientific computing)

## How MCP Works

- An MCP server exposes tools, resources, and prompts
- An MCP client (AI assistant) connects to the server
- The client discovers available capabilities
- When the user asks a question, the AI can:
  1. Decide which tools to use
  2. Call the tools with appropriate parameters
  3. Receive results
  4. Incorporate results into its response
- All communication happens via the MCP protocol (typically over stdio or HTTP)

## Next Steps

- In the next lecture, we'll implement an MCP server that exposes our Flask API as tools
- We'll learn about async programming and HTTP streaming
- We'll connect our MCP server to Claude Desktop and Cursor

