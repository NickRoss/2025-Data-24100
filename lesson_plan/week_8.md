# Week #8 Lesson Plan

## Overview

- Wednesday night the next part of the project is due (Part VI). You can find the assignment [here](../project_assignments/part_6.md).
- There will be a quiz on Wednesday covering material up to and including the previous week.
- This week we will cover Docker Compose and begin our introduction to MCP (Model Context Protocol).

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Networking](https://docs.docker.com/network/)
- Lecture examples: `lecture_examples/15_testing` and `lecture_examples/16_compose`

## Learning Objectives

### Testing Review (from Day 14)

- Review pytest fixtures and test structure
- Understand how sequential tests work with pytest-order
- Review schema validation with jsonschema

### Docker Compose Introduction

- Understand the motivation for Docker Compose (multiple services, orchestration)
- Recognize when to use Docker Compose vs. single Docker containers
- Understand the structure of a `docker-compose.yml` file:
  - Services definition
  - Build context and Dockerfiles
  - Port mappings
  - Volume mounts
  - Environment variables
  - Networks
  - Dependencies (`depends_on`)

### Docker Compose Commands

- `docker compose up` - Start services
- `docker compose down` - Stop and remove services
- `docker compose ps` - List running containers
- `docker compose logs` - View logs
- `docker compose run` - Run a one-off command in a service
- `docker compose build` - Build images
- `docker kill <container-name>` - Forcefully stop a container (not a compose command, but useful for stopping individual containers)

### Container Networking

- Understand how containers communicate within a Docker Compose network
- Know how to reference other services by service name
- Understand the difference between host networking and bridge networking

### Migration from Single Container to Compose

- Understand the changes required to convert a single-container setup to Docker Compose
- Recognize how Makefiles change when using Docker Compose
- Understand how to structure projects for multi-container environments

### LLMs, Agents, and MCP Introduction

- Understand what Large Language Models (LLMs) are and their limitations
- Understand what AI Agents are and how they differ from simple LLM queries
- Recognize the role of tools in agentic systems
- Understand the agent loop: observe → think → act → observe
- Understand what MCP is and why it was created
- Understand the relationship between MCP servers and MCP clients
- Recognize MCP as a protocol for connecting AI assistants to external tools and data sources
- Understand key MCP concepts: tools, resources, prompts, sampling
- Understand why MCP uses HTTP streaming (SSE) instead of REST

## Lecture notes

- [Day 15 (Testing Part II & Docker Compose)](../class_notes/15_testing_part_2.md)
- [Day 16 (LLMs, Agents, and MCP)](../class_notes/16_llms_agents_mcp.md)

## Quizzable Concepts

### Testing Review

- How do you ensure tests run in a specific order with pytest?
- What is the purpose of `@pytest.mark.order()`?
- How do you share state between sequential tests?

### Docker Compose

- What is Docker Compose and why would you use it instead of multiple `docker run` commands?
- What are the main sections of a `docker-compose.yml` file?
- How do you start all services defined in a docker-compose.yml file?
- How do you stop and remove all containers created by docker compose?
- How do containers in the same Docker Compose network communicate with each other?
- What is the difference between `docker compose up` and `docker compose run`?
- How do you view logs from a specific service in Docker Compose?
- What does `depends_on` do in a docker-compose.yml file?
- What is the difference between `docker compose down` and `docker kill`?

### LLMs, Agents, and MCP

- What is the difference between an LLM query and an AI agent?
- What is the "agent loop"?
- What role do tools play in agentic systems?
- What does MCP stand for and what is its purpose?
- What are the main components that an MCP server can expose? (tools, resources, prompts)
- What is the relationship between an MCP server and an MCP client?
- Why would you use MCP instead of a REST API for AI agent interactions?
- What is HTTP streaming and why does MCP use it?
