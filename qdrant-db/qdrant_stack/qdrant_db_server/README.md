# Qdrant Vector Database for LLM Retrieval

This is a production-level setup of Qdrant Vector Database optimized for LLM retrieval applications.

## Installation and Setup

1. Initialize the environment:

```bash
# Create directories and copy config
mkdir -p /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/config
mkdir -p /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/storage
mkdir -p /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/snapshots
cp /Users/frank/mcp_servers/qdrant-db/reference_repos/qdrant/config/config.yaml /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/config/production.yaml
```

2. Set up the optimization configuration:

```bash
./scripts/update_config.sh
```

3. Start the Qdrant server:

```bash
./scripts/manage.sh start
```

4. Create a FastEmbed collection:

```bash
./scripts/manage.sh setup
```

5. Load data (example):

```bash
./scripts/load_data.py --json your_documents.json --collection llm_documents
```

## Management

Use the management script for common operations:

```bash
./scripts/manage.sh [command]
```

Available commands:
- `start` - Start Qdrant server
- `stop` - Stop Qdrant server
- `restart` - Restart Qdrant server
- `status` - Check server status
- `logs` - Show server logs
- `backup [collection]` - Create backup of a collection
- `collections` - List collections
- `monitor` - Show monitoring information
- `performance` - Run performance tests
- `setup` - Set up FastEmbed collection

## Performance Testing

Run performance tests to evaluate query response times:

```bash
./scripts/performance_test.py --collection llm_documents --iterations 10
```

## Data Loading

Load documents from a JSON file:

```bash
./scripts/load_data.py --json documents.json --text-field content
```

## Monitoring

Monitor the Qdrant server:

```bash
./scripts/monitor.sh
```

## Backups

Create a backup of a collection:

```bash
./scripts/backup.sh llm_documents
```

## Dependencies

Make sure you have the following Python dependencies installed:

```bash
pip install qdrant-client fastembed
```

For optimal performance with FastEmbed, ensure you have the appropriate Pytorch installations.
