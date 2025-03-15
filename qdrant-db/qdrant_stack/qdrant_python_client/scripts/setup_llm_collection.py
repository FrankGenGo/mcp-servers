#!/usr/bin/env python3
"""
Script to set up an LLM-optimized Qdrant collection with hybrid search.
"""

import logging
import argparse
import sys
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_COLLECTION_NAME = "llm_documents"
DEFAULT_DENSE_MODEL = "BAAI/bge-small-en"  # Use the client's default model for consistency
DEFAULT_SPARSE_MODEL = "Qdrant/bm25"  # BM25 sparse model for keyword matching

def get_client():
    """Create and return a QdrantClient instance"""
    host = os.environ.get("QDRANT_HOST", "localhost")
    port = int(os.environ.get("QDRANT_PORT", 6333))
    grpc_port = int(os.environ.get("QDRANT_GRPC_PORT", 6334))
    prefer_grpc = os.environ.get("QDRANT_PREFER_GRPC", "True").lower() == "true"
    
    try:
        client = QdrantClient(
            host=host,
            port=port,
            grpc_port=grpc_port,
            prefer_grpc=prefer_grpc
        )
        # Test connection
        client.get_collections()
        logger.info(f"Connected to Qdrant at {host}:{port}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {str(e)}")
        raise

def setup_hybrid_collection(
    client,
    collection_name=DEFAULT_COLLECTION_NAME,
    dense_model=DEFAULT_DENSE_MODEL,
    sparse_model=DEFAULT_SPARSE_MODEL,
    force=False
):
    """
    Set up a collection optimized for LLM document retrieval with hybrid search.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of the collection to create
        dense_model: Name of the dense embedding model to use
        sparse_model: Name of the sparse embedding model to use
        force: If True, will drop and recreate existing collection
    
    Returns:
        bool: True if successful
    """
    try:
        # Check if collection already exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name in collection_names:
            if force:
                logger.info(f"Dropping existing collection: {collection_name}")
                client.delete_collection(collection_name)
            else:
                logger.info(f"Collection {collection_name} already exists")
                return True
        
        # Set up the embedding models
        # Set the dense model first
        client.set_model(dense_model)
        logger.info(f"Set dense embedding model: {dense_model}")
        
        # Set sparse model if provided
        if sparse_model:
            client.set_sparse_model(sparse_model)
            logger.info(f"Set sparse embedding model: {sparse_model}")
        
        # Create a sample document to get vector parameters automatically
        sample_docs = ["This is a sample document for initializing the collection."]
        sample_metadata = [{"source": "initialization"}]
        # Use a simple integer ID instead of a string (avoids UUID parsing issues with gRPC)
        sample_ids = [1]
        
        # Let FastEmbed handle the collection creation with the right parameters
        client.add(
            collection_name=collection_name,
            documents=sample_docs,
            metadata=sample_metadata,
            ids=sample_ids
        )
        
        # Now that collection is created, update its configuration for optimal LLM retrieval
        client.update_collection(
            collection_name=collection_name,
            hnsw_config={
                "m": 16,  # Number of connections per node (higher allows better recall but uses more memory)
                "ef_construct": 200,  # Controls index creation quality vs speed (higher is more accurate but slower)
                "full_scan_threshold": 10000  # Use brute force for small collections
            },
            optimizers_config={
                "default_segment_number": 2,  # Number of segments for new data
                "indexing_threshold": 20000,  # Minimal number of vectors for on-disk index
                "memmap_threshold": 20000  # Minimal number of vectors for memmap
            }
            # Note: on_disk_payload can only be set during initial collection creation
        )
        
        # Delete initialization point (optional)
        client.delete(
            collection_name=collection_name,
            points_selector=sample_ids
        )
        
        logger.info(f"Created LLM-optimized collection: {collection_name}")
        logger.info(f"Collection is ready for hybrid search with both dense and sparse vectors")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up collection: {str(e)}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Set up an LLM-optimized Qdrant collection")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME, help="Name of the collection to create")
    parser.add_argument("--dense-model", default=DEFAULT_DENSE_MODEL, help="Dense embedding model to use")
    parser.add_argument("--sparse-model", default=DEFAULT_SPARSE_MODEL, help="Sparse embedding model to use")
    parser.add_argument("--force", action="store_true", help="Force recreation of collection if it exists")
    args = parser.parse_args()
    
    try:
        # Create client
        client = get_client()
        
        # Set up collection
        success = setup_hybrid_collection(
            client=client,
            collection_name=args.collection,
            dense_model=args.dense_model,
            sparse_model=args.sparse_model,
            force=args.force
        )
        
        if success:
            logger.info("Collection setup completed successfully")
            sys.exit(0)
        else:
            logger.error("Collection setup failed")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)