# Qdrant MCP Inspector Dashboard

This project provides a Docker-based deployment of the Model Context Protocol (MCP) Inspector Dashboard, configured to integrate with our Qdrant Vector Database and Qdrant MCP Server.

![MCP Inspector Screenshot](mcp-inspector.png)

## Project Overview

This Inspector Dashboard allows us to:

1. Connect to the Qdrant MCP Server running on our Docker network
2. Test vector search functionality
3. Debug MCP protocol communications
4. Visualize resources and tools provided by our Qdrant MCP server

## Docker Setup

The project uses Docker and Docker Compose to create a containerized environment that connects to our existing Qdrant Docker network.

### Running with Docker

```bash
# Build the Docker container
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

## Container Network Integration

The inspector container is configured to join the Qdrant network, allowing direct communication with:

- Qdrant Database Server: `http://qdrant-server:6333`
- Qdrant MCP Server: `http://qdrant-mcp-server:8000`

### Qdrant MCP Architecture

Our setup integrates the following components:

1. **Qdrant Database Server**: A vector database for storing and retrieving embeddings
2. **Qdrant MCP Server**: A Model Context Protocol server that exposes vector search capabilities
3. **MCP Inspector**: A dashboard for testing and debugging MCP interactions

The Inspector connects to the Qdrant MCP server via the Server-Sent Events (SSE) transport protocol and allows us to:

- List and test vector search tools provided by the Qdrant MCP server
- View resources and their content
- Send prompts and sampling requests
- Debug communication between MCP components

## Accessing the Inspector

Once running, access the Inspector UI at:
- Inspector UI: http://localhost:5173
- MCP Proxy Server: http://localhost:3000

## Development

For local development without Docker:

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build
npm start
```

## Python Virtual Environment and Testing

The Docker container includes a Python virtual environment at `/app/venv` with several testing utilities. To work with them:

1. Activate the virtual environment inside the container:
   ```bash
   source /app/venv/bin/activate
   ```

2. Run the connection test script:
   ```bash
   python /app/scripts/test_qdrant_connection.py
   ```

3. Test using the MCP client library:
   ```bash
   python /app/scripts/mcp_client_test.py
   ```

4. Query Qdrant directly for vector search:
   ```bash
   python /app/scripts/test_qdrant_query.py "your search query"
   ```

You can also run these scripts from the host using the management script:
```bash
# Test connections
./scripts/manage.sh exec python /app/scripts/test_qdrant_connection.py

# Test MCP client
./scripts/manage.sh exec python /app/scripts/mcp_client_test.py

# Perform vector search query
./scripts/manage.sh exec python /app/scripts/test_qdrant_query.py "vector search query"
```

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.
