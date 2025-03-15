#\!/usr/bin/env python3
"""
Performance testing script for Qdrant LLM retrieval
"""

import time
import argparse
from typing import List
import statistics

from qdrant_client import QdrantClient

def test_query_performance(
    queries: List[str],
    collection_name: str = "llm_documents",
    limit: int = 10,
    iterations: int = 5
):
    """
    Test query performance with multiple iterations
    
    Args:
        queries: List of queries to test
        collection_name: Collection to query
        limit: Number of results to retrieve
        iterations: Number of iterations for each query
    """
    client = QdrantClient(host="localhost", port=6333)
    
    # Ensure models are loaded
    print("Setting up embedding models...")
    client.set_model("BAAI/bge-base-en-v1.5")
    client.set_sparse_model("jina-embeddings-v2-small-en")
    
    # Warmup
    print("Warming up...")
    for query in queries[:1]:
        client.query(
            collection_name=collection_name,
            query_text=query,
            limit=limit
        )
    
    # Single query tests
    print("\n=== Single Query Performance ===")
    for query in queries:
        times = []
        for i in range(iterations):
            start = time.time()
            client.query(
                collection_name=collection_name,
                query_text=query,
                limit=limit
            )
            elapsed = (time.time() - start) * 1000  # ms
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"Query: '{query}'")
        print(f"  Avg: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
    
    # Batch query test
    print("\n=== Batch Query Performance ===")
    times = []
    for i in range(iterations):
        start = time.time()
        client.query_batch(
            collection_name=collection_name,
            query_texts=queries,
            limit=limit
        )
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    per_query = avg_time / len(queries)
    
    print(f"Batch of {len(queries)} queries:")
    print(f"  Avg total: {avg_time:.2f}ms, Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
    print(f"  Avg per query: {per_query:.2f}ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Qdrant query performance")
    parser.add_argument("--collection", default="llm_documents", help="Collection name")
    parser.add_argument("--limit", type=int, default=10, help="Number of results to retrieve")
    parser.add_argument("--iterations", type=int, default=5, help="Number of test iterations")
    
    args = parser.parse_args()
    
    # Sample queries
    test_queries = [
        "How does machine learning work?",
        "What are the benefits of vector databases?",
        "Explain the concept of semantic search",
        "How to implement RAG with LLMs?",
        "What is the difference between dense and sparse embeddings?"
    ]
    
    test_query_performance(
        queries=test_queries,
        collection_name=args.collection,
        limit=args.limit,
        iterations=args.iterations
    )
