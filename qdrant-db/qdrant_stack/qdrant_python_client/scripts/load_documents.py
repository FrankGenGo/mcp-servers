#!/usr/bin/env python3
"""
Script to load documents into a Qdrant collection.
Optimized for LLM retrieval with chunking and metadata handling.
"""

import logging
import argparse
import sys
import os
import json
import uuid
from typing import List, Dict, Any, Optional, Union
import time

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default values
DEFAULT_COLLECTION_NAME = "llm_documents"
DEFAULT_CHUNK_SIZE = 512  # Characters
DEFAULT_CHUNK_OVERLAP = 128  # Characters
DEFAULT_BATCH_SIZE = 64  # Documents per batch

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
        
        # Set the same models as in setup_llm_collection.py for consistency
        client.set_model("BAAI/bge-small-en")
        client.set_sparse_model("Qdrant/bm25")
        
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {str(e)}")
        raise

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

def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load documents from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Ensure data is a list of documents
        if isinstance(data, dict):
            if "documents" in data:
                return data["documents"]
            elif "items" in data:
                return data["items"]
            else:
                return [data]  # Single document
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unexpected JSON format in {file_path}")
    
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise

def load_documents(
    client: QdrantClient,
    documents: List[Dict[str, Any]],
    collection_name: str = DEFAULT_COLLECTION_NAME,
    text_field: str = "text",
    id_field: Optional[str] = None,
    metadata_fields: Optional[List[str]] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    batch_size: int = DEFAULT_BATCH_SIZE
) -> List[str]:
    """
    Load documents into Qdrant collection, optimized for LLM retrieval.
    
    Args:
        client: QdrantClient instance
        documents: List of document dictionaries
        collection_name: Name of the collection to load into
        text_field: Field name containing the document text
        id_field: Field name to use as document ID (if None, generate UUIDs)
        metadata_fields: List of field names to include in metadata
        chunk_size: Size of text chunks in characters
        chunk_overlap: Overlap between chunks in characters
        batch_size: Number of points to upload in a batch
    
    Returns:
        List of generated document IDs
    """
    # Check if collection exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    if collection_name not in collection_names:
        logger.error(f"Collection {collection_name} does not exist. Please create it first.")
        return []
    
    # Process documents
    all_doc_ids = []
    batch_points = []
    total_chunks = 0
    start_time = time.time()
    
    for doc in documents:
        # Extract text
        if text_field not in doc:
            logger.warning(f"Skipping document without '{text_field}' field: {doc}")
            continue
        
        text = doc[text_field]
        
        # Extract ID
        if id_field and id_field in doc:
            doc_id = str(doc[id_field])
        else:
            doc_id = str(uuid.uuid4())
        
        all_doc_ids.append(doc_id)
        
        # Extract metadata
        metadata = {}
        if metadata_fields:
            for field in metadata_fields:
                if field in doc and field != text_field:
                    metadata[field] = doc[field]
        
        # Add source document info
        metadata["doc_id"] = doc_id
        metadata["source"] = doc.get("source", "unknown")
        
        # Chunk document
        chunks = chunk_text(text, chunk_size, chunk_overlap)
        
        # Create points for each chunk
        for i, chunk in enumerate(chunks):
            # Create unique ID for chunk
            if len(chunks) == 1:
                chunk_id = doc_id
            else:
                chunk_id = f"{doc_id}_{i}"
            
            # Prepare metadata for this chunk
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_idx": i,
                "total_chunks": len(chunks),
                "text": chunk,  # Store text for easy retrieval
                "text_len": len(chunk)
            })
            
            # Create point structure (embedding will be handled by client.add)
            point = {
                "id": chunk_id,
                "payload": chunk_metadata,
                "document": chunk  # This will be converted to embedding via FastEmbed
            }
            
            batch_points.append(point)
            total_chunks += 1
            
            # Upload batch if it reaches the batch size
            if len(batch_points) >= batch_size:
                try:
                    client.add(
                        collection_name=collection_name,
                        documents=[p["document"] for p in batch_points],
                        metadata=[p["payload"] for p in batch_points],
                        ids=[p["id"] for p in batch_points]
                    )
                    logger.info(f"Uploaded batch of {len(batch_points)} chunks")
                except Exception as e:
                    logger.error(f"Error uploading batch: {str(e)}")
                
                batch_points = []
    
    # Upload any remaining points
    if batch_points:
        try:
            client.add(
                collection_name=collection_name,
                documents=[p["document"] for p in batch_points],
                metadata=[p["payload"] for p in batch_points],
                ids=[p["id"] for p in batch_points]
            )
            logger.info(f"Uploaded final batch of {len(batch_points)} chunks")
        except Exception as e:
            logger.error(f"Error uploading final batch: {str(e)}")
    
    elapsed = time.time() - start_time
    logger.info(f"Completed loading {len(all_doc_ids)} documents ({total_chunks} chunks) in {elapsed:.2f} seconds")
    
    return all_doc_ids

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Load documents into Qdrant collection")
    parser.add_argument("--file", required=True, help="JSON file containing documents to load")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME, help="Collection name")
    parser.add_argument("--text-field", default="text", help="Field containing document text")
    parser.add_argument("--id-field", help="Field to use as document ID (default: generate UUIDs)")
    parser.add_argument("--metadata-fields", help="Comma-separated list of metadata fields to include")
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP, help="Chunk overlap in characters")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Upload batch size")
    args = parser.parse_args()
    
    try:
        # Parse metadata fields
        metadata_fields = None
        if args.metadata_fields:
            metadata_fields = [f.strip() for f in args.metadata_fields.split(",")]
        
        # Create client
        client = get_client()
        
        # Load JSON documents
        documents = load_json_file(args.file)
        logger.info(f"Loaded {len(documents)} documents from {args.file}")
        
        # Load documents into Qdrant
        doc_ids = load_documents(
            client=client,
            documents=documents,
            collection_name=args.collection,
            text_field=args.text_field,
            id_field=args.id_field,
            metadata_fields=metadata_fields,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            batch_size=args.batch_size
        )
        
        if doc_ids:
            logger.info(f"Successfully loaded {len(doc_ids)} documents into collection {args.collection}")
            sys.exit(0)
        else:
            logger.error("Failed to load documents")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)