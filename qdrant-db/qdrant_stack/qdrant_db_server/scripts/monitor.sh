#\!/bin/bash
# Simple monitoring script for Qdrant server

echo "=== Telemetry ==="
curl -s http://localhost:6333/telemetry | jq

echo "=== Collections ==="
curl -s http://localhost:6333/collections | jq

echo "=== Docker Status ==="
docker stats qdrant-server --no-stream
