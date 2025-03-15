# MCP Inspector Development Guide

## Build Commands

- Build all: `npm run build`
- Build client: `npm run build-client`
- Build server: `npm run build-server`
- Development mode: `npm run dev` (use `npm run dev:windows` on Windows)
- Format code: `npm run prettier-fix`
- Client lint: `cd client && npm run lint`

## Docker Commands
- Build container: `docker-compose build`
- Start container: `docker-compose up -d`
- Stop container: `docker-compose down`
- View logs: `docker-compose logs -f`

## Code Style Guidelines

- Use TypeScript with proper type annotations
- Follow React functional component patterns with hooks
- Use ES modules (import/export) not CommonJS
- Use Prettier for formatting (auto-formatted on commit)
- Follow existing naming conventions:
  - camelCase for variables and functions
  - PascalCase for component names and types
  - kebab-case for file names
- Use async/await for asynchronous operations
- Implement proper error handling with try/catch blocks
- Use Tailwind CSS for styling in the client
- Keep components small and focused on a single responsibility

## Project Organization

The project is organized as a monorepo with workspaces:

- `client/`: React frontend with Vite, TypeScript and Tailwind
- `server/`: Express backend with TypeScript
- `bin/`: CLI scripts

## Qdrant Integration

This MCP Inspector is configured to connect to the Qdrant MCP server running in the Docker network. Connection details:

- Inspector UI: http://localhost:5173
- MCP Proxy Server: http://localhost:3000
- Qdrant MCP Server: http://qdrant-mcp-server:8000
- Qdrant Database: http://qdrant-server:6333

The Docker configuration connects to the Qdrant network defined in `/Users/frank/mcp_servers/qdrant-db/qdrant_stack/docker-compose.yml`.
