#!/usr/bin/env python3
"""
Script to query documents from a Qdrant collection.
Optimized for LLM retrieval with hybrid search.
"""

import logging
import argparse
import sys
import os
import json
import time
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, SearchParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default values
DEFAULT_COLLECTION_NAME = "llm_documents"
DEFAULT_LIMIT = 10
DEFAULT_HYBRID_ALPHA = 0.7  # Weight for dense vectors in hybrid search (0-1)
# Default HNSW search ef parameter (can be passed directly instead of using SearchParams)
DEFAULT_HNSW_EF = 128  # Higher gives better recall at cost of latency

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
        
        # Set FastEmbed model for both dense and sparse vectors
        try:
            # Set the same model that was used in setup
            client.set_model("BAAI/bge-small-en")
            # Set sparse model for hybrid search
            client.set_sparse_model("Qdrant/bm25")
            logger.info("FastEmbed models set successfully for hybrid search")
        except Exception as e:
            logger.warning(f"Failed to set FastEmbed models: {str(e)}")
        
        # Test connection
        client.get_collections()
        logger.info(f"Connected to Qdrant at {host}:{port}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {str(e)}")
        raise

def parse_filter(filter_json: str) -> Optional[Filter]:
    """Parse a filter from JSON string"""
    if not filter_json:
        return None
    
    try:
        filter_dict = json.loads(filter_json)
        return build_filter(filter_dict)
    except Exception as e:
        logger.error(f"Error parsing filter JSON: {str(e)}")
        return None

def build_filter(filter_dict: Dict[str, Any]) -> Filter:
    """Build a Qdrant filter from a dictionary"""
    filter_args = {}
    
    for filter_type in ["must", "should", "must_not"]:
        if filter_type in filter_dict:
            conditions = []
            for condition in filter_dict[filter_type]:
                if "key" in condition:
                    field_condition = None
                    
                    # Match condition
                    if "match" in condition:
                        field_condition = FieldCondition(
                            key=condition["key"],
                            match=MatchValue(value=condition["match"]["value"])
                        )
                    
                    # Range condition
                    elif "range" in condition:
                        range_dict = condition["range"]
                        field_condition = FieldCondition(
                            key=condition["key"],
                            range=Range(**range_dict)
                        )
                    
                    if field_condition:
                        conditions.append(field_condition)
            
            if conditions:
                filter_args[filter_type] = conditions
    
    return Filter(**filter_args)

def query_documents(
    client: QdrantClient,
    query_text: str,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    limit: int = DEFAULT_LIMIT,
    filter_obj: Optional[Filter] = None,
    with_payload: bool = True,
    hybrid: bool = True,
    hybrid_alpha: float = DEFAULT_HYBRID_ALPHA,
    hnsw_ef: int = DEFAULT_HNSW_EF,
    exact: bool = False
):
    """
    Query documents from a Qdrant collection using semantic search with FastEmbed.
    Note: This function uses client.query() which returns QueryResponse objects,
    not ScoredPoint objects as from client.search().
    """
    """
    Query documents from a Qdrant collection using semantic search.
    
    Args:
        client: QdrantClient instance
        query_text: Query text to search for
        collection_name: Name of the collection to search
        limit: Maximum number of results to return
        filter_obj: Optional filter to apply
        with_payload: Whether to return the document payload
        hybrid: Whether to use hybrid search (dense + sparse)
        hybrid_alpha: Weight of dense vectors in hybrid search (0-1)
        search_params: Search parameters
    
    Returns:
        List of document results
    """
    # Validate collection exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    if collection_name not in collection_names:
        logger.error(f"Collection {collection_name} does not exist")
        return []
    
    # We're not using search_params as a separate parameter anymore
    
    try:
        # Perform search
        start_time = time.time()
        
        # Use only the documented parameters
        common_params = {
            "collection_name": collection_name,
            "query_text": query_text,
            "query_filter": filter_obj,
            "limit": limit,
        }
        
        # Check if hybrid search is supported by looking at sparse_embedding_model_name
        has_sparse_model = False
        try:
            has_sparse_model = hasattr(client, 'sparse_embedding_model_name') and client.sparse_embedding_model_name is not None
        except:
            pass
            
        # When both dense and sparse models are set, hybrid search happens automatically
        if has_sparse_model and hybrid:
            logger.info(f"Using hybrid search with sparse model: {client.sparse_embedding_model_name}")
            search_type = "hybrid"
        else:
            if hybrid:
                logger.warning("No sparse model set, using standard dense vector search")
            search_type = "dense"
            
        try:
            # Perform the query with just the basic parameters
            results = client.query(**common_params)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            results = []
        
        elapsed = time.time() - start_time
        logger.info(f"{search_type.capitalize()} search found {len(results)} results in {elapsed:.4f} seconds")
        
        return results
    
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        return []

def format_results(results, output_format="text"):
    """Format search results in specified format"""
    if not results:
        return f"Found 0 results:"
        
    if output_format == "json":
        # Output as JSON
        output = []
        for i, result in enumerate(results):
            # Extract relevant information from the result
            item = {
                "id": getattr(result, 'id', 'Unknown'),
                "score": getattr(result, 'score', 0.0)
            }
            
            # For QueryResponse from client.query()
            if hasattr(result, 'document'):
                doc = result.document
                if isinstance(doc, str):
                    item["text"] = doc
                elif isinstance(doc, dict):
                    item.update(doc)
            
            # For ScoredPoint from client.search()
            elif hasattr(result, 'payload') and result.payload:
                item.update(result.payload)
            
            output.append(item)
        
        return json.dumps(output, indent=2)
    
    else:
        # Output as formatted text
        lines = []
        lines.append(f"Found {len(results)} results:")
        lines.append("")
        
        for i, result in enumerate(results):
            id_value = getattr(result, 'id', 'Unknown')
            score_value = getattr(result, 'score', 0.0)
            
            lines.append(f"Result {i+1} (Score: {score_value:.4f}, ID: {id_value}):")
            
            # For QueryResponse from client.query()
            if hasattr(result, 'document'):
                doc = result.document
                if isinstance(doc, str):
                    lines.append(f"Text: {doc[:200]}..." if len(doc) > 200 else f"Text: {doc}")
                elif isinstance(doc, dict):
                    # Include text directly if available
                    if "text" in doc:
                        text = doc["text"]
                        lines.append(f"Text: {text[:200]}..." if len(text) > 200 else f"Text: {text}")
                    
                    # Add metadata
                    metadata_items = []
                    for k, v in doc.items():
                        if k not in ["text", "text_len"]:
                            metadata_items.append(f"{k}: {v}")
                    
                    if metadata_items:
                        metadata = ", ".join(metadata_items)
                        lines.append(f"Metadata: {metadata}")
            
            # For ScoredPoint from client.search()
            elif hasattr(result, 'payload') and result.payload:
                payload = result.payload
                if "text" in payload:
                    text = payload["text"]
                    lines.append(f"Text: {text[:200]}..." if len(text) > 200 else f"Text: {text}")
                
                # Add metadata
                metadata_items = []
                for k, v in payload.items():
                    if k not in ["text", "text_len"]:
                        metadata_items.append(f"{k}: {v}")
                
                if metadata_items:
                    metadata = ", ".join(metadata_items)
                    lines.append(f"Metadata: {metadata}")
            
            lines.append("")
        
        return "\n".join(lines)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Query documents from Qdrant collection")
    parser.add_argument("--query", required=True, help="Query text to search for")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION_NAME, help="Collection name")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum number of results")
    parser.add_argument("--filter", help="JSON filter string")
    parser.add_argument("--hybrid", action="store_true", default=True, help="Use hybrid search")
    parser.add_argument("--no-hybrid", action="store_false", dest="hybrid", help="Disable hybrid search")
    parser.add_argument("--alpha", type=float, default=DEFAULT_HYBRID_ALPHA, help="Hybrid search alpha (0-1)")
    parser.add_argument("--hnsw-ef", type=int, default=DEFAULT_HNSW_EF, help="HNSW ef search parameter")
    parser.add_argument("--exact", action="store_true", help="Use exact search (slower but more accurate)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    try:
        # Create client
        client = get_client()
        
        # Parse filter if provided
        filter_obj = parse_filter(args.filter) if args.filter else None
        
        # Query documents
        results = query_documents(
            client=client,
            query_text=args.query,
            collection_name=args.collection,
            limit=args.limit,
            filter_obj=filter_obj,
            hybrid=args.hybrid,
            hybrid_alpha=args.alpha,
            hnsw_ef=args.hnsw_ef,
            exact=args.exact
        )
        
        # Format results
        output = format_results(results, args.format)
        
        # Output results
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Results written to {args.output}")
        else:
            print(output)
        
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)