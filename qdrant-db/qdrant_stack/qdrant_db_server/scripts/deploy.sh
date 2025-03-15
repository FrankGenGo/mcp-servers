#\!/bin/bash
# Pull latest image
docker pull qdrant/qdrant

# Run with optimized production configuration
docker run -d --name qdrant-server \
  -p 6333:6333 -p 6334:6334 \
  -v /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/storage:/qdrant/storage \
  -v /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/snapshots:/qdrant/snapshots \
  -v /Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/config/production.yaml:/qdrant/config/production.yaml \
  --restart unless-stopped \
  qdrant/qdrant
