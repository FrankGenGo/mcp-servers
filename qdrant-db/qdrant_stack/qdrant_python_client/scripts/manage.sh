#!/bin/bash
# Management script for Qdrant Python client operations

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
COLLECTION_NAME="llm_documents"
DENSE_MODEL="BAAI/bge-base-en-v1.5"
SPARSE_MODEL="jina-embeddings-v2-small-en"

# Function to display help message
show_help() {
    echo "Qdrant Client Management Script"
    echo "-------------------------------"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  test-connection    Test connection to Qdrant server"
    echo "  setup-collection   Create a new collection optimized for LLM retrieval"
    echo "  load-documents     Load documents into a collection"
    echo "  query             Search for documents in a collection"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test-connection"
    echo "  $0 setup-collection --name my_collection --force"
    echo "  $0 load-documents --file documents.json --collection my_collection"
    echo "  $0 query --query \"What is vector search?\" --collection my_collection --limit 5"
    echo ""
}

# Function to run a Python script with the provided arguments
run_python_script() {
    SCRIPT_NAME="$1"
    shift
    python3 "$SCRIPT_DIR/$SCRIPT_NAME" "$@"
    return $?
}

# Process commands
if [[ $# -eq 0 || "$1" == "help" || "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    test-connection)
        echo "Testing connection to Qdrant server..."
        run_python_script "test_connection.py"
        ;;
        
    setup-collection)
        # Parse additional arguments
        NAME="$COLLECTION_NAME"
        FORCE=""
        
        while [[ "$#" -gt 0 ]]; do
            case "$1" in
                --name)
                    NAME="$2"
                    shift 2
                    ;;
                --force)
                    FORCE="--force"
                    shift
                    ;;
                --dense-model)
                    DENSE_MODEL="$2"
                    shift 2
                    ;;
                --sparse-model)
                    SPARSE_MODEL="$2"
                    shift 2
                    ;;
                *)
                    echo "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        echo "Setting up collection: $NAME"
        run_python_script "setup_llm_collection.py" --collection "$NAME" --dense-model "$DENSE_MODEL" --sparse-model "$SPARSE_MODEL" $FORCE
        ;;
        
    load-documents)
        # No additional processing needed; just pass all arguments to the script
        echo "Loading documents..."
        run_python_script "load_documents.py" "$@"
        ;;
        
    query)
        # No additional processing needed; just pass all arguments to the script
        echo "Querying documents..."
        run_python_script "query_documents.py" "$@"
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

# Display result of command
if [ $? -eq 0 ]; then
    echo "Command completed successfully."
else
    echo "Command failed with error code $?."
    exit 1
fi