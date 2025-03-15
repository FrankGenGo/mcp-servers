#!/usr/bin/env python3
"""
Test script to interact with the MCP server and verify the complete data flow.
"""

import asyncio
import json
from mcp.client import SimpleMcpClient

async def main():
    # Connect to the MCP server
    client = SimpleMcpClient("http://localhost:8000")
    await client.connect()
    print("Connected to MCP server")

    # Store data (Test LLM -> MCP -> Qdrant flow)
    print("\nStoring information in Qdrant...")
    store_response = await client.run_tool(
        "qdrant-store",
        {
            "information": "The Qdrant vector database is designed for semantic search and efficient vector retrieval.",
            "metadata": {"source": "test_script", "important": True}
        }
    )
    print(f"Store response: {store_response}")

    # Add more test data
    await client.run_tool(
        "qdrant-store",
        {
            "information": "Python is a programming language with a focus on readability and simplicity.",
            "metadata": {"source": "test_script", "topic": "programming"}
        }
    )
    
    await client.run_tool(
        "qdrant-store",
        {
            "information": "Neural networks are a set of algorithms designed to recognize patterns.",
            "metadata": {"source": "test_script", "topic": "AI"}
        }
    )

    # Search for information (Test MCP -> Qdrant retrieval flow)
    print("\nSearching for information about Qdrant...")
    search_response = await client.run_tool(
        "qdrant-find",
        {"query": "vector database"}
    )
    print(f"Search response: {json.dumps(search_response, indent=2)}")

    print("\nSearching for information about Python...")
    search_response = await client.run_tool(
        "qdrant-find",
        {"query": "programming language"}
    )
    print(f"Search response: {json.dumps(search_response, indent=2)}")

    # Close the connection
    await client.close()
    print("\nDisconnected from MCP server")

if __name__ == "__main__":
    asyncio.run(main())