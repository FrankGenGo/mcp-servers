#\!/usr/bin/env python3
"""
Data Loading Utility for Qdrant
This script provides functions to load documents into Qdrant with FastEmbed integration.
"""

import argparse
import json
import time
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient

def load_documents(
    documents: List[str],
    metadata: Optional[List[Dict[str, Any]]] = None,
    collection_name: str = "llm_documents",
    dense_model: str = "BAAI/bge-base-en-v1.5",
    sparse_model: Optional[str] = "jina-embeddings-v2-small-en",
    batch_size: int = 64,
    parallel: int = 4
):
    """
    Load documents into Qdrant with FastEmbed integration.
    
    Args:
        documents: List of document texts to embed and store
        metadata: Optional metadata for each document
        collection_name: Name of the collection to store documents in
        dense_model: FastEmbed model for dense vectors
        sparse_model: FastEmbed model for sparse vectors (or None to disable)
        batch_size: Number of documents to process in each batch
        parallel: Number of parallel workers for embedding
    
    Returns:
        List of document IDs
    """
    client = QdrantClient(host="localhost", port=6333)
    
    # Set up embedding models
    print(f"Setting up dense embedding model: {dense_model}")
    client.set_model(dense_model)
    
    if sparse_model:
        print(f"Setting up sparse embedding model: {sparse_model}")
        client.set_sparse_model(sparse_model)
    
    # Load documents
    start_time = time.time()
    print(f"Loading {len(documents)} documents into collection '{collection_name}'...")
    
    ids = client.add(
        collection_name=collection_name,
        documents=documents,
        metadata=metadata,
        batch_size=batch_size,
        parallel=parallel
    )
    
    elapsed = time.time() - start_time
    print(f"Loaded {len(documents)} documents in {elapsed:.2f} seconds")
    print(f"Average time per document: {(elapsed/len(documents))*1000:.2f} ms")
    
    return ids

def load_from_json(
    json_file: str,
    text_field: str = "text",
    collection_name: str = "llm_documents",
    dense_model: str = "BAAI/bge-base-en-v1.5",
    sparse_model: Optional[str] = "jina-embeddings-v2-small-en"
):
    """
    Load documents from a JSON file.
    
    Args:
        json_file: Path to JSON file with documents
        text_field: Field in each JSON object containing the document text
        collection_name: Name of the collection to store documents in
        dense_model: FastEmbed model for dense vectors
        sparse_model: FastEmbed model for sparse vectors (or None to disable)
    
    Returns:
        List of document IDs
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        documents = [item[text_field] for item in data if text_field in item]
        # Use the rest of the fields as metadata
        metadata = [{k: v for k, v in item.items() if k \!= text_field} for item in data]
    else:
        raise ValueError("JSON file must contain a list of objects")
    
    return load_documents(
        documents=documents,
        metadata=metadata,
        collection_name=collection_name,
        dense_model=dense_model,
        sparse_model=sparse_model
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load documents into Qdrant")
    parser.add_argument("--json", help="Path to JSON file with documents")
    parser.add_argument("--text-field", default="text", help="Field containing document text")
    parser.add_argument("--collection", default="llm_documents", help="Collection name")
    parser.add_argument("--dense-model", default="BAAI/bge-base-en-v1.5", help="Dense embedding model")
    parser.add_argument("--sparse-model", default="jina-embeddings-v2-small-en", 
                        help="Sparse embedding model (or 'none' to disable)")
    
    args = parser.parse_args()
    
    if args.json:
        sparse_model = None if args.sparse_model.lower() == 'none' else args.sparse_model
        load_from_json(
            json_file=args.json,
            text_field=args.text_field,
            collection_name=args.collection,
            dense_model=args.dense_model,
            sparse_model=sparse_model
        )
    else:
        parser.print_help()
