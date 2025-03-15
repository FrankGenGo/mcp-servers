#!/usr/bin/env python3
"""
Retriever module for Qdrant client.
Optimized for retrieving documents for LLM context.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, SearchParams
from client import get_client, DEFAULT_COLLECTION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default search parameters
DEFAULT_LIMIT = 10
DEFAULT_SEARCH_PARAMS = SearchParams(
    hnsw_ef=128,  # Higher values improve recall at the cost of latency
    exact=False  # Set to True for better recall but slower performance
)
HYBRID_ALPHA = 0.7  # Weight of dense vectors in hybrid search (0-1)

def retrieve_documents(
    query_text: str,
    collection_name: str = DEFAULT_COLLECTION,
    limit: int = DEFAULT_LIMIT,
    filter_condition: Optional[Dict[str, Any]] = None,
    client: Optional[QdrantClient] = None,
    search_params: Optional[SearchParams] = None,
    hybrid: bool = True,
    hybrid_alpha: float = HYBRID_ALPHA,
    with_payload: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve documents from Qdrant using semantic search, optimized for LLM context retrieval.
    
    Args:
        query_text: The query text to search for
        collection_name: Name of the collection to search in
        limit: Maximum number of results to return
        filter_condition: Optional filter condition to apply
        client: QdrantClient instance, created if None
        search_params: Optional search parameters
        hybrid: Whether to use hybrid search (dense + sparse)
        hybrid_alpha: Weight of dense vectors in hybrid search (0-1)
        with_payload: Whether to return the document payload
    
    Returns:
        List of retrieved documents with scores
    """
    if client is None:
        client = get_client()
    
    if search_params is None:
        search_params = DEFAULT_SEARCH_PARAMS
    
    # Build filter if provided
    filter_obj = None
    if filter_condition:
        filter_obj = build_filter(filter_condition)
    
    # Perform search
    try:
        if hybrid:
            # Use the hybrid API which combines dense and sparse vectors
            results = client.query(
                collection_name=collection_name,
                query_text=query_text,
                query_filter=filter_obj,
                limit=limit,
                search_params=search_params,
                with_payload=with_payload,
                alpha=hybrid_alpha
            )
        else:
            # Use standard search with just dense vectors
            results = client.query(
                collection_name=collection_name,
                query_text=query_text,
                query_filter=filter_obj,
                limit=limit,
                search_params=search_params,
                with_payload=with_payload
            )
        
        # Process results
        documents = []
        for result in results:
            doc = {
                "id": result.id,
                "score": result.score
            }
            
            if with_payload and result.payload:
                doc.update({"payload": result.payload})
                
                # For convenience, add the text directly if available
                if "text" in result.payload:
                    doc["text"] = result.payload["text"]
            
            documents.append(doc)
        
        return documents
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise

def build_filter(filter_dict: Dict[str, Any]) -> Filter:
    """
    Build a Qdrant filter from a dictionary.
    
    Args:
        filter_dict: Dictionary with filter conditions
    
    Returns:
        Filter object
    """
    # Examples of filter_dict:
    # {"must": [{"key": "metadata.source", "match": {"value": "website"}}]}
    # {"should": [{"key": "metadata.year", "range": {"gte": 2020}}]}
    
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

def retrieve_for_llm_context(
    query_text: str,
    max_tokens: int = 2000,
    client: Optional[QdrantClient] = None,
    collection_name: str = DEFAULT_COLLECTION,
    initial_limit: int = 20,
    filter_condition: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Retrieve documents and format them for LLM context, ensuring token limit.
    
    Args:
        query_text: The query text to search for
        max_tokens: Maximum number of tokens to return (estimated)
        client: QdrantClient instance, created if None
        collection_name: Name of the collection to search in
        initial_limit: Initial number of documents to retrieve
        filter_condition: Optional filter condition to apply
    
    Returns:
        Formatted context for LLM
    """
    # Retrieve documents
    docs = retrieve_documents(
        query_text=query_text,
        collection_name=collection_name,
        limit=initial_limit,
        filter_condition=filter_condition,
        client=client,
        hybrid=True,
        with_payload=True
    )
    
    # Estimate tokens (rough approximation: 4 chars ≈ 1 token)
    CHARS_PER_TOKEN = 4
    token_budget = max_tokens * CHARS_PER_TOKEN
    
    # Build context string with token budget in mind
    context = []
    used_chars = 0
    
    for doc in docs:
        if "text" in doc:
            text = doc["text"]
            source = doc.get("payload", {}).get("source", "Unknown source")
            doc_id = doc.get("id", "Unknown ID")
            
            # Format the document context
            doc_context = f"Document ID: {doc_id}\nSource: {source}\nContent: {text}\n\n"
            
            if used_chars + len(doc_context) <= token_budget:
                context.append(doc_context)
                used_chars += len(doc_context)
            else:
                # If we can't fit the whole document, try to fit a truncated version
                remaining_chars = token_budget - used_chars
                if remaining_chars > 100:  # Only add if we can include meaningful content
                    truncated = doc_context[:remaining_chars-3] + "..."
                    context.append(truncated)
                break
    
    return "".join(context)

if __name__ == "__main__":
    # Example usage
    client = get_client()
    
    # Test retrieval
    query = "What is Qdrant vector database?"
    results = retrieve_documents(
        query_text=query,
        client=client,
        limit=5
    )
    
    print(f"Query: {query}")
    print(f"Results: {len(results)}")
    
    for i, doc in enumerate(results):
        print(f"\nResult {i+1} (Score: {doc['score']:.4f}):")
        if "text" in doc:
            print(doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"])
    
    # Test LLM context retrieval
    llm_context = retrieve_for_llm_context(
        query_text=query,
        client=client
    )
    
    print("\nLLM Context:")
    print(llm_context[:500] + "..." if len(llm_context) > 500 else llm_context)