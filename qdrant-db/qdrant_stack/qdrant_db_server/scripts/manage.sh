#\!/bin/bash
# Qdrant management script

QDRANT_DIR="/Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server"

function show_usage() {
  echo "Qdrant Management Script"
  echo "Usage: ./manage.sh [command]"
  echo ""
  echo "Commands:"
  echo "  start       - Start Qdrant server"
  echo "  stop        - Stop Qdrant server"
  echo "  restart     - Restart Qdrant server"
  echo "  status      - Check server status"
  echo "  logs        - Show server logs"
  echo "  backup      - Create backup of a collection"
  echo "  collections - List collections"
  echo "  monitor     - Show monitoring information"
  echo "  performance - Run performance tests"
  echo "  setup       - Set up FastEmbed collection"
}

case "$1" in
  start)
    echo "Starting Qdrant server..."
    ${QDRANT_DIR}/scripts/deploy.sh
    ;;
  stop)
    echo "Stopping Qdrant server..."
    docker stop qdrant-server
    ;;
  restart)
    echo "Restarting Qdrant server..."
    docker stop qdrant-server
    docker rm qdrant-server
    ${QDRANT_DIR}/scripts/deploy.sh
    ;;
  status)
    echo "Checking Qdrant server status..."
    docker ps -f name=qdrant-server
    ;;
  logs)
    echo "Showing Qdrant server logs..."
    docker logs qdrant-server
    ;;
  backup)
    if [ -z "$2" ]; then
      echo "Usage: ./manage.sh backup <collection_name>"
      exit 1
    fi
    echo "Creating backup of collection $2..."
    ${QDRANT_DIR}/scripts/backup.sh "$2"
    ;;
  collections)
    echo "Listing collections..."
    curl -s http://localhost:6333/collections | jq
    ;;
  monitor)
    echo "Running monitoring..."
    ${QDRANT_DIR}/scripts/monitor.sh
    ;;
  performance)
    echo "Running performance tests..."
    ${QDRANT_DIR}/scripts/performance_test.py
    ;;
  setup)
    echo "Setting up FastEmbed collection..."
    ${QDRANT_DIR}/scripts/fastembed_setup.py
    ;;
  *)
    show_usage
    ;;
esac
