# Qdrant MCP Server

This is a Model Context Protocol (MCP) server for Qdrant Vector Database that allows semantic search using the MCP protocol.

## Configuration

The server is configured using environment variables:

- `QDRANT_URL`: URL of the Qdrant server (default: "http://qdrant-database:6333")
- `QDRANT_API_KEY`: API key for the Qdrant server (if required)
- `COLLECTION_NAME`: Name of the collection to use (default: "llm_documents")
- `EMBEDDING_MODEL`: Name of the embedding model to use (default: "sentence-transformers/all-MiniLM-L6-v2")
- `LOG_LEVEL`: Logging level (default: "INFO")

## Running with Docker

The server is designed to run in Docker using Docker Compose:

```bash
docker-compose up -d
```

## Local Development

For local development outside of Docker:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Run the server:
   ```bash
   QDRANT_URL="http://localhost:6333" \
   COLLECTION_NAME="llm_documents" \
   python -m mcp_server_qdrant.main --transport sse
   ```

## MCP Tools

This server provides the following MCP tools:

1. `qdrant-store`: Store information in the Qdrant database
2. `qdrant-find`: Search for information in the Qdrant database