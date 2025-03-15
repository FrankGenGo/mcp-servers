# MCP Servers Monorepo

This repository contains a collection of services and tools for working with the Model Context Protocol (MCP).

## Components

### Inspector
A dashboard for inspecting and interacting with MCP servers. Built with React/Vite frontend and Express backend.

- Located in: `/inspector`
- Features:
  - Connect to MCP servers
  - Explore available tools
  - Test prompts
  - Query vector stores

### Qdrant-DB
Vector database implementation using Qdrant with MCP server integration.

- Located in: `/qdrant-db`
- Features:
  - MCP server for Qdrant
  - Python client for document operations
  - FastEmbed integration for vector embeddings

### MCP Docker Network
Docker network configuration for connecting MCP services.

- Located in: `/mcp-docker-network`

## Getting Started

1. Ensure Docker and Docker Compose are installed
2. Start the services:
   ```bash
   cd inspector
   docker-compose up -d
   ```
   ```bash
   cd qdrant-db/qdrant_stack
   docker-compose up -d
   ```

3. Access the Inspector dashboard at http://localhost:5173

## Architecture

The services communicate over a shared Docker network:

- Inspector dashboard (port 5173) → Express proxy (port 3000) → Qdrant MCP server (port 8000)
- Qdrant MCP server → Qdrant database (port 6333)

## Development

Each component can be developed independently. See the README in each subdirectory for specific development instructions.