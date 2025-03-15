#!/usr/bin/env python3
"""
Document loader for Qdrant client.
Optimized for loading and chunking text for LLM retrieval.
"""

import logging
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Union
import os
import json

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SparseVector
from client import get_client, DEFAULT_COLLECTION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants for text chunking
DEFAULT_CHUNK_SIZE = 512  # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 128  # Overlap between chunks

def chunk_text(
    text: str, 
    chunk_size: int = DEFAULT_CHUNK_SIZE, 
    overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into chunks of specified size with overlap.
    
    Args:
        text: The text to split
        chunk_size: Maximum chunk size in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find a good breaking point (end of sentence if possible)
        end = min(start + chunk_size, len(text))
        
        # Try to find sentence boundary
        if end < len(text):
            # Look for period, question mark, or exclamation point followed by space or newline
            for i in range(end-1, max(start+chunk_size//2, start), -1):
                if text[i] in '.!?\n' and (i+1 >= len(text) or text[i+1].isspace()):
                    end = i + 1
                    break
        
        # Add the chunk
        chunks.append(text[start:end].strip())
        
        # Move to next chunk with overlap
        start = end - overlap
    
    return chunks

def load_documents(
    documents: List[str],
    metadata: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[Union[str, int, uuid.UUID]]] = None,
    client: Optional[QdrantClient] = None,
    collection_name: str = DEFAULT_COLLECTION,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    batch_size: int = 100
) -> List[str]:
    """
    Load documents into Qdrant, optimized for LLM retrieval.
    
    Args:
        documents: List of text documents to load
        metadata: Optional list of metadata dictionaries, one per document
        ids: Optional list of IDs, one per document
        client: QdrantClient instance, created if None
        collection_name: Name of the collection to load into
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        batch_size: Number of points to upload in a batch
    
    Returns:
        List of generated IDs
    """
    if client is None:
        client = get_client()
    
    # Initialize metadata list if not provided
    if metadata is None:
        metadata = [{} for _ in documents]
    elif len(metadata) != len(documents):
        raise ValueError(f"Metadata length ({len(metadata)}) must match documents length ({len(documents)})")
    
    # Initialize IDs if not provided
    if ids is None:
        ids = [str(uuid.uuid4()) for _ in documents]
    elif len(ids) != len(documents):
        raise ValueError(f"IDs length ({len(ids)}) must match documents length ({len(documents)})")
    
    # Process documents in batches
    all_points = []
    all_chunk_ids = []
    
    for i, (doc, meta, doc_id) in enumerate(zip(documents, metadata, ids)):
        # Chunk the document
        chunks = chunk_text(doc, chunk_size, chunk_overlap)
        
        for chunk_idx, chunk in enumerate(chunks):
            # Create a unique ID for the chunk
            if len(chunks) == 1:
                chunk_id = str(doc_id)
            else:
                chunk_id = f"{doc_id}_{chunk_idx}"
            
            all_chunk_ids.append(chunk_id)
            
            # Create metadata for the chunk
            chunk_meta = meta.copy()
            chunk_meta.update({
                "doc_id": str(doc_id),
                "chunk_idx": chunk_idx,
                "total_chunks": len(chunks),
                "text": chunk,  # Store the text for easy retrieval
                "text_len": len(chunk)
            })
            
            # Create point (embedding will be done by the client)
            point = PointStruct(
                id=chunk_id,
                payload=chunk_meta,
                vector={"dense": None}  # Will be filled by the client
            )
            
            all_points.append(point)
            
            if len(all_points) >= batch_size:
                # Upload batch
                client.add(
                    collection_name=collection_name,
                    points=all_points
                )
                logger.info(f"Uploaded {len(all_points)} document chunks to {collection_name}")
                all_points = []
    
    # Upload any remaining points
    if all_points:
        client.add(
            collection_name=collection_name,
            points=all_points
        )
        logger.info(f"Uploaded {len(all_points)} document chunks to {collection_name}")
    
    return all_chunk_ids

def load_json_documents(
    json_file: str,
    text_field: str = "text",
    metadata_fields: Optional[List[str]] = None,
    id_field: Optional[str] = None,
    **kwargs
) -> List[str]:
    """
    Load documents from a JSON file into Qdrant.
    
    Args:
        json_file: Path to JSON file containing documents
        text_field: Field name containing the document text
        metadata_fields: List of field names to include in metadata
        id_field: Field name to use as document ID
        **kwargs: Additional arguments to pass to load_documents
    
    Returns:
        List of generated IDs
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Ensure data is a list
    if not isinstance(data, list):
        if isinstance(data, dict) and "items" in data:
            data = data["items"]
        else:
            data = [data]
    
    documents = []
    metadata = []
    ids = []
    
    for item in data:
        # Extract text
        if text_field not in item:
            logger.warning(f"Skipping item without '{text_field}' field: {item}")
            continue
        
        documents.append(item[text_field])
        
        # Extract metadata
        meta = {}
        if metadata_fields:
            for field in metadata_fields:
                if field in item and field != text_field:
                    meta[field] = item[field]
        metadata.append(meta)
        
        # Extract ID
        if id_field and id_field in item:
            ids.append(item[id_field])
        else:
            ids.append(str(uuid.uuid4()))
    
    return load_documents(
        documents=documents,
        metadata=metadata,
        ids=ids,
        **kwargs
    )

if __name__ == "__main__":
    # Example usage
    client = get_client()
    
    # Test with a small document
    sample_documents = [
        "This is a sample document for testing LLM retrieval. This document contains information about Qdrant, "
        "which is a vector database designed for storing and querying vector embeddings. "
        "It's particularly useful for semantic search, recommendation systems, and AI applications."
    ]
    
    sample_metadata = [
        {"source": "example", "author": "Qdrant Team", "date": "2023-01-01"}
    ]
    
    sample_ids = [str(uuid.uuid4())]
    
    load_documents(
        documents=sample_documents,
        metadata=sample_metadata,
        ids=sample_ids,
        client=client
    )