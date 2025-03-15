# Qdrant Python Client

This is a Python client for connecting to and working with the Qdrant vector database. It's optimized for LLM retrieval applications, supporting both dense and sparse vectors for hybrid search.

## Features

- Connection to Qdrant server via REST and gRPC
- FastEmbed integration for easy document embedding
- Collection management with optimized settings for LLM retrieval
- Document loading with automatic chunking
- Hybrid search capabilities combining dense and sparse vectors
- Docker integration for containerized deployment

## Directory Structure

```
qdrant_python_client/
├── Dockerfile            # Dockerfile for containerized deployment
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── scripts/
    ├── client.py         # Client connection module (was merged with other modules)
    ├── load_documents.py # Script for loading and chunking documents
    ├── manage.sh         # Management script for common operations
    ├── query_documents.py # Script for searching documents
    ├── sample_documents.json # Sample documents for testing
    ├── setup_llm_collection.py # Script for creating LLM-optimized collections
    └── test_connection.py # Script for testing server connection
```

## Installation

### Docker (Recommended)

The client can be built and run using Docker Compose:

```bash
cd /Users/frank/mcp_servers/qdrant-db/qdrant_stack
docker-compose build qdrant-client
docker-compose up -d qdrant-client
```

### Local Installation

To install the client locally:

```bash
pip install -r requirements.txt
```

## Usage

### Management Script

The `manage.sh` script provides a convenient interface for common operations:

```bash
# Test connection to Qdrant server
./scripts/manage.sh test-connection

# Create a collection optimized for LLM retrieval
./scripts/manage.sh setup-collection --name my_collection

# Load documents into a collection
./scripts/manage.sh load-documents --file scripts/sample_documents.json --collection my_collection

# Query documents
./scripts/manage.sh query --query "What is vector search?" --collection my_collection --limit 5
```

### Python API

You can also use the Python scripts directly:

```python
from scripts.setup_llm_collection import get_client, setup_hybrid_collection
from scripts.load_documents import load_documents, load_json_file
from scripts.query_documents import query_documents

# Connect to Qdrant
client = get_client()

# Create a collection
setup_hybrid_collection(client, collection_name="my_collection")

# Load documents
docs = load_json_file("scripts/sample_documents.json")
load_documents(client, docs, collection_name="my_collection")

# Query documents
results = query_documents(
    client=client,
    query_text="What is vector search?",
    collection_name="my_collection",
    limit=5,
    hybrid=True
)

# Print results
for i, result in enumerate(results):
    print(f"Result {i+1} (Score: {result.score:.4f}): {result.payload['text'][:100]}...")
```

## Environment Variables

The following environment variables can be used to configure the client:

- `QDRANT_HOST`: Hostname of the Qdrant server (default: "localhost")
- `QDRANT_PORT`: HTTP port of the Qdrant server (default: 6333)
- `QDRANT_GRPC_PORT`: gRPC port of the Qdrant server (default: 6334)
- `QDRANT_PREFER_GRPC`: Whether to prefer gRPC over HTTP (default: "True")

## Docker Network

When running in Docker, the client connects to the Qdrant server container using the Docker network. The Docker Compose configuration sets up a shared network (`qdrant-network`) for the client and server containers, allowing them to communicate using container names as hostnames.