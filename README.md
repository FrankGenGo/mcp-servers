# MCP Servers Multi-Agent AI Infrastructure

A comprehensive infrastructure for enabling multi-agent AI swarms powered by specialized Model Context Protocol (MCP) servers. This monorepo contains the full stack of components needed to orchestrate, connect, and empower intelligent agents with various specialized capabilities.

## 🌟 Overview

This project enables the creation of a multi-agent AI ecosystem where specialized agents can collaborate, share context, and leverage different capabilities through the Model Context Protocol (MCP). By providing a standardized communication layer, agents can seamlessly access vector databases, specialized tools, and various data sources through a unified protocol.

The infrastructure supports:
- Semantic search and retrieval through vector embeddings
- Multi-agent collaboration and communication
- Modular, microservice-based architecture
- Visual inspection and debugging of agent interactions
- Extensible tool frameworks for AI capabilities

## 🧩 Core Components

### Inspector
An interactive dashboard for monitoring, testing, and debugging MCP servers. Built with React/Vite frontend and Express backend.

- Located in: `/inspector`
- Features:
  - Real-time connection to any MCP server
  - Interactive exploration of available tools
  - Test prompts and tool invocations
  - Monitor agent interactions
  - Debug server responses and behavior

### Qdrant-DB with MCP Integration
Vector database implementation using Qdrant with full MCP server integration, enabling semantic search capabilities for AI agents.

- Located in: `/qdrant-db`
- Features:
  - Vector embeddings for semantic similarity search
  - Document storage with metadata
  - Python client for advanced operations
  - FastEmbed integration for efficient embeddings
  - Seamless connection to the MCP ecosystem

### MCP Docker Network
Infrastructure for orchestrating and connecting MCP services in a unified network.

- Located in: `/mcp-docker-network`
- Features:
  - Isolated network for secure service communication
  - Management tools for container orchestration
  - Service discovery within the swarm
  - Simplified deployment of complex agent systems

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js (for local development)
- Python 3.9+ (for running clients and scripts)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/FrankGenGo/mcp-servers.git
   cd mcp-servers
   ```

2. Set up the shared Docker network:
   ```bash
   cd mcp-docker-network
   ./scripts/manage-network.sh create
   ```

3. Start the Qdrant vector database and MCP server:
   ```bash
   cd ../qdrant-db/qdrant_stack
   docker-compose up -d
   ```

4. Start the Inspector dashboard:
   ```bash
   cd ../../inspector
   docker build -t mcp-inspector .
   docker run -d --name mcp-inspector --network mcp-docker-network -p 5173:5173 -p 3000:3000 mcp-inspector
   ```

5. Access the Inspector dashboard at http://localhost:5173

## 🏗️ Architecture

This project implements a distributed microservices architecture centered around the Model Context Protocol:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   AI Agent    │     │  AI Agent     │     │  AI Agent     │
│  Capabilities │     │  Reasoning    │     │  Planning     │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │                     ▼                     │
        │             ┌───────────────┐             │
        └────────────►  MCP Network   ◄─────────────┘
                     │ Communication  │
                     └───────┬───────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼──────────┐        ┌─────────▼──────────┐
    │   Qdrant MCP       │        │  Inspector         │
    │   Vector Search    │        │  Monitoring        │
    └────────────────────┘        └────────────────────┘
```

Components communicate over a shared Docker network, with:
- Inspector dashboard (port 5173) → Express proxy (port 3000) → MCP servers
- Qdrant MCP server (port 8000) → Qdrant database (port 6333)
- All services connected via the `mcp-docker-network`

## 🧠 Use Cases

- **Multi-Agent Systems**: Build collaborative agent systems that combine different AI capabilities
- **Knowledge Management**: Create semantic search systems with intuitive AI interfaces
- **Tool Integration**: Extend AI capabilities with specialized tools and data sources
- **Development & Debugging**: Inspect and test MCP servers during development

## 🛠️ Development

Each component can be developed independently:

- **Inspector**: React/TypeScript frontend with Express backend
- **Qdrant MCP Server**: Python FastMCP implementation
- **Network Management**: Bash scripts and Docker Compose configurations

See the README in each subdirectory for specific development instructions.

## 📚 Further Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.