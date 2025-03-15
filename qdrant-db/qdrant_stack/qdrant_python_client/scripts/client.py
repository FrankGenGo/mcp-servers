#!/usr/bin/env python3
"""
Main Qdrant client script for connecting to the Qdrant server.
Optimized for LLM vector retrieval and the Model Context Protocol.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default embedding model configuration
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"  # Powerful and efficient model for LLM retrieval
DEFAULT_EMBEDDING_DIM = 768  # Dimension for DEFAULT_EMBEDDING_MODEL
DEFAULT_SPARSE_MODEL = "jina-embeddings-v2-small-en"  # For hybrid search
DEFAULT_COLLECTION = "llm_documents"

def get_client():
    """
    Create and return a QdrantClient instance connected to the Qdrant server.
    
    By default, connects to the Qdrant server running in a Docker container.
    Environment variables can be used to configure the connection.
    """
    # Get connection details from environment variables or use defaults
    host = os.environ.get("QDRANT_HOST", "localhost")
    port = int(os.environ.get("QDRANT_PORT", 6333))
    grpc_port = int(os.environ.get("QDRANT_GRPC_PORT", 6334))
    prefer_grpc = os.environ.get("QDRANT_PREFER_GRPC", "True").lower() == "true"
    
    # Connect to Qdrant server
    try:
        client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc
        )
        
        # If FastEmbed is available, set the default embedding model
        try:
            client.set_model(DEFAULT_EMBEDDING_MODEL)
            logger.info(f"Using FastEmbed model: {DEFAULT_EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"FastEmbed model setup failed: {str(e)}")
            
        logger.info(f"Connected to Qdrant server at {host}:{port} (gRPC: {grpc_port})")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant server: {str(e)}")
        raise

def create_llm_collection(client, collection_name=DEFAULT_COLLECTION, overwrite=False):
    """
    Create a collection optimized for LLM document retrieval with hybrid search.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of the collection to create
        overwrite: If True, will drop existing collection with same name
    
    Returns:
        True if collection was created or already exists
    """
    # Check if collection already exists
    collections = client.get_collections()
    collection_names = [collection.name for collection in collections.collections]
    
    if collection_name in collection_names:
        if overwrite:
            logger.info(f"Dropping existing collection: {collection_name}")
            client.delete_collection(collection_name)
        else:
            logger.info(f"Collection {collection_name} already exists")
            return True
    
    # Create collection with both dense and sparse vectors for hybrid search
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": VectorParams(
                size=DEFAULT_EMBEDDING_DIM,
                distance=Distance.COSINE,
                on_disk=True  # Store vectors on disk for larger collections
            ),
            "sparse": VectorParams(
                size=DEFAULT_EMBEDDING_DIM,  # Will be ignored for sparse vectors
                distance=Distance.DOT,  # For sparse vectors, DOT product is used
            )
        },
        # Set optimal parameters for LLM retrieval
        hnsw_config={
            "m": 16,  # Number of connections per node (higher allows better recall but uses more memory)
            "ef_construct": 200,  # Controls index creation quality vs speed (higher is more accurate but slower)
            "full_scan_threshold": 10000  # Use brute force for small collections
        },
        optimizers_config={
            "default_segment_number": 2,  # Number of segments for new data
            "indexing_threshold": 20000,  # Minimal number of vectors for on-disk index
            "memmap_threshold": 20000  # Minimal number of vectors for memmap
        },
        on_disk_payload=True  # Store payload on disk to handle larger document collections
    )
    
    logger.info(f"Created LLM-optimized collection: {collection_name}")
    return True

if __name__ == "__main__":
    # Test connection
    client = get_client()
    collections = client.get_collections()
    logger.info(f"Available collections: {[c.name for c in collections.collections]}")
    
    # Create default LLM collection if it doesn't exist
    create_llm_collection(client)