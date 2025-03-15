#!/usr/bin/env python3
"""
Test script for Qdrant client connection.
"""

import os
import logging
import time
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to Qdrant server"""
    # Get connection details from environment variables or use defaults
    host = os.environ.get("QDRANT_HOST", "localhost")
    port = int(os.environ.get("QDRANT_PORT", 6333))
    grpc_port = int(os.environ.get("QDRANT_GRPC_PORT", 6334))
    prefer_grpc = os.environ.get("QDRANT_PREFER_GRPC", "True").lower() == "true"
    
    # Log connection parameters
    logger.info(f"Connecting to Qdrant at {host}:{port} (gRPC: {grpc_port}, prefer_grpc: {prefer_grpc})")
    
    # Create client
    try:
        client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc
        )
        
        # Test connection by getting collections
        collections = client.get_collections()
        logger.info(f"Connection successful! Found {len(collections.collections)} collections.")
        
        return client
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return None

def test_fastembed_integration(client):
    """Test FastEmbed integration by creating a collection and adding a document"""
    if client is None:
        logger.error("Cannot test FastEmbed integration without a client connection")
        return False
    
    try:
        # First, set the model
        model_name = "BAAI/bge-small-en"  # Use a smaller model for testing
        client.set_model(model_name)
        logger.info(f"FastEmbed model set to {model_name}")
        
        # Collection name for testing
        collection_name = "test_fastembed"
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name in collection_names:
            logger.info(f"Collection {collection_name} already exists. Recreating...")
            client.delete_collection(collection_name)
        
        # The most reliable approach is to let the client create the collection automatically
        # when adding documents. This ensures all vector params match the model's requirements.
        docs = ["This is a test document for Qdrant with FastEmbed integration"]
        metadata = [{"source": "test"}]
        ids = [1]
        
        # This will automatically create a collection with the correct vector config
        client.add(
            collection_name=collection_name,
            documents=docs,
            metadata=metadata,
            ids=ids
        )
        logger.info("Added test document using FastEmbed (collection created automatically)")
        
        # Try waiting a moment for indexing
        import time
        time.sleep(1)
        
        # Search for the document
        search_result = client.query(
            collection_name=collection_name,
            query_text="test document"
        )
        
        if len(search_result) > 0:
            logger.info(f"Search successful! Found {len(search_result)} results.")
            logger.info(f"Top result score: {search_result[0].score}")
            return True
        else:
            logger.error("Search returned no results.")
            return False
            
    except Exception as e:
        logger.error(f"FastEmbed test failed: {e}")
        return False

def wait_for_qdrant_server(max_retries=10, retry_interval=5):
    """Wait for the Qdrant server to become available"""
    for i in range(max_retries):
        logger.info(f"Attempt {i+1}/{max_retries} to connect to Qdrant server...")
        client = test_connection()
        if client:
            return client
        
        if i < max_retries - 1:
            logger.info(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
    
    logger.error(f"Failed to connect after {max_retries} attempts")
    return None

if __name__ == "__main__":
    # Wait for Qdrant server to be ready (important in Docker environment)
    client = wait_for_qdrant_server()
    
    if client:
        # Test FastEmbed integration
        success = test_fastembed_integration(client)
        
        if success:
            logger.info("All tests passed! The Qdrant client is properly configured and connected.")
            sys.exit(0)
        else:
            logger.error("FastEmbed integration test failed.")
            sys.exit(1)
    else:
        logger.error("Failed to connect to Qdrant server.")
        sys.exit(1)