#\!/usr/bin/env python3
"""
Qdrant FastEmbed Setup Script
This script sets up a Qdrant collection with FastEmbed integration for LLM retrieval.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

def setup_collection(collection_name="llm_documents", dense_model="BAAI/bge-base-en-v1.5", 
                    sparse_model="jina-embeddings-v2-small-en"):
    """Set up a Qdrant collection with FastEmbed integration"""
    
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(collection.name == collection_name for collection in collections)
    
    if collection_exists:
        print(f"Collection '{collection_name}' already exists")
        return client
    
    # Set up dense model
    print(f"Setting up dense embedding model: {dense_model}")
    client.set_model(dense_model)
    
    # Create collection with FastEmbed config
    vectors_config = client.get_fastembed_vector_params(
        on_disk=False  # Keep in RAM for speed
    )
    
    # Set up sparse model if provided
    sparse_vectors_config = None
    if sparse_model:
        print(f"Setting up sparse embedding model: {sparse_model}")
        client.set_sparse_model(sparse_model)
        sparse_vectors_config = client.get_fastembed_sparse_vector_params(
            on_disk=False
        )
    
    # Create the collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=vectors_config,
        sparse_vectors_config=sparse_vectors_config,
    )
    
    print(f"Successfully created collection '{collection_name}' with FastEmbed integration")
    print(f"Dense model: {dense_model}")
    if sparse_model:
        print(f"Sparse model: {sparse_model}")
    
    return client

if __name__ == "__main__":
    setup_collection()
