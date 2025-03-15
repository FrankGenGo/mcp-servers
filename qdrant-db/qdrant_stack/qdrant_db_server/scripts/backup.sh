#\!/bin/bash
# Backup script for Qdrant collections

if [ -z "$1" ]; then
  echo "Usage: ./backup.sh <collection_name>"
  exit 1
fi

COLLECTION=$1
BACKUP_DIR="/Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/backups"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

mkdir -p "$BACKUP_DIR/$TIMESTAMP"

echo "Creating snapshot of collection $COLLECTION..."
curl -X POST "http://localhost:6333/collections/$COLLECTION/snapshots"

echo "Downloading latest snapshot..."
curl -X GET "http://localhost:6333/collections/$COLLECTION/snapshots/latest" \
     -o "$BACKUP_DIR/$TIMESTAMP/$COLLECTION-snapshot.zip"

echo "Backup completed: $BACKUP_DIR/$TIMESTAMP/$COLLECTION-snapshot.zip"
