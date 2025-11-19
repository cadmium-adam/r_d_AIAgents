import asyncio
import json
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """
    ChromaDB MCP Client Demo

    Demonstrates vector database operations using ChromaDB MCP server
    connecting to Docker ChromaDB instance at localhost:8100
    """

    print("🚀 Starting ChromaDB MCP Client Demo")
    print("=" * 60)

    # MCP server STDIO
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "chroma-mcp",
            "--client-type",
            "http",
            "--host",
            "localhost",
            "--port",
            "8100",
            "--ssl",
            "false",
        ],
    )

    try:
        async with stdio_client(server_params) as stdio_transport:
            async with ClientSession(*stdio_transport) as session:
                # Initialize session
                print("🔄 Initializing MCP session...")
                result = await session.initialize()
                print("✅ MCP session initialized successfully!")

                # Test ping
                ping_result = await session.send_ping()
                print(f"📡 Ping result: {ping_result}")

                # List available tools
                print("\n📋 Available ChromaDB Tools:")
                tools_list_response = await session.list_tools()
                for tool in tools_list_response.tools:
                    print(f"  • {tool.name}: {tool.description}")

                print("\n" + "=" * 60)

                # Step 1: List existing collections
                print("🔍 Step 1: Listing existing collections...")
                collections_response = await session.call_tool("chroma_list_collections", {})

                try:
                    collections = json.loads(collections_response.content[0].text)
                    print(f"Found {len(collections)} existing collections:")
                    for collection in collections:
                        print(
                            f"  • {collection['name'] if isinstance(collection, dict) else collection}"
                        )
                except json.JSONDecodeError:
                    # Handle non-JSON response
                    collections_text = collections_response.content[0].text
                    if "NO_COLLECTIONS_FOUND" in collections_text:
                        collections = []
                        print("Found 0 existing collections (database is empty)")
                    else:
                        # Try to parse as simple list
                        collections = (
                            collections_text.strip().split("\n") if collections_text.strip() else []
                        )
                        print(f"Found {len(collections)} existing collections:")
                        for collection in collections:
                            print(f"  • {collection}")

                # Step 2: Create a new collection for our demo
                collection_name = f"ai_knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"\n📦 Step 2: Creating collection '{collection_name}'...")

                create_response = await session.call_tool(
                    "chroma_create_collection",
                    {
                        "collection_name": collection_name,
                        "metadata": {
                            "description": "AI and ML knowledge base for MCP demo",
                            "created_by": "mcp_demo",
                            "version": "1.0",
                        },
                    },
                )
                print("✅ Collection created successfully!")

                # Step 3: Add sample documents with metadata
                print("\n📄 Step 3: Adding sample documents...")

                sample_documents = [
                    {
                        "id": "doc_1",
                        "document": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without explicit programming.",
                        "metadata": {
                            "category": "machine_learning",
                            "difficulty": "beginner",
                            "tags": "AI,ML,basics",
                            "author": "demo",
                        },
                    },
                    {
                        "id": "doc_2",
                        "document": "Deep learning uses neural networks with multiple layers to model and understand complex patterns in large datasets, enabling breakthroughs in image recognition and natural language processing.",
                        "metadata": {
                            "category": "deep_learning",
                            "difficulty": "intermediate",
                            "tags": "deep_learning,neural_networks,NLP",
                            "author": "demo",
                        },
                    },
                    {
                        "id": "doc_3",
                        "document": "Vector databases store and retrieve high-dimensional vector embeddings, enabling semantic search and similarity matching for AI applications.",
                        "metadata": {
                            "category": "databases",
                            "difficulty": "intermediate",
                            "tags": "vectors,embeddings,search",
                            "author": "demo",
                        },
                    },
                    {
                        "id": "doc_4",
                        "document": "Large Language Models like GPT and Claude are transformer-based neural networks trained on vast amounts of text data to understand and generate human-like text.",
                        "metadata": {
                            "category": "language_models",
                            "difficulty": "advanced",
                            "tags": "LLM,transformers,GPT,Claude",
                            "author": "demo",
                        },
                    },
                    {
                        "id": "doc_5",
                        "document": "Retrieval Augmented Generation (RAG) combines information retrieval with language generation, allowing AI models to access external knowledge bases.",
                        "metadata": {
                            "category": "rag",
                            "difficulty": "advanced",
                            "tags": "RAG,retrieval,generation,knowledge",
                            "author": "demo",
                        },
                    },
                ]

                for doc in sample_documents:
                    add_response = await session.call_tool(
                        "chroma_add_documents",
                        {
                            "collection_name": collection_name,
                            "documents": [doc["document"]],
                            "metadatas": [doc["metadata"]],
                            "ids": [doc["id"]],
                        },
                    )
                    print(f"  ✅ Added document: {doc['id']}")

                # Step 4: Get collection info
                print(f"\n📊 Step 4: Collection '{collection_name}' statistics...")
                info_response = await session.call_tool(
                    "chroma_get_collection_info", {"collection_name": collection_name}
                )
                try:
                    info = json.loads(info_response.content[0].text)
                    print(f"  • Total documents: {info.get('count', 'N/A')}")
                    print(f"  • Collection metadata: {info.get('metadata', {})}")
                except json.JSONDecodeError:
                    print(f"  • Collection info: {info_response.content[0].text}")

                # Step 5: Semantic search queries
                print("\n🔍 Step 5: Performing semantic search queries...")

                queries = [
                    {
                        "query": "How do neural networks learn from data?",
                        "description": "Query about neural network learning",
                    },
                    {
                        "query": "What are embedding vectors used for?",
                        "description": "Query about vector embeddings",
                    },
                    {
                        "query": "How do modern AI chatbots work?",
                        "description": "Query about conversational AI",
                    },
                ]

                for i, query_info in enumerate(queries, 1):
                    print(f"\n  Query {i}: {query_info['description']}")
                    print(f"  Question: '{query_info['query']}'")

                    query_response = await session.call_tool(
                        "chroma_query_documents",
                        {
                            "collection_name": collection_name,
                            "query_texts": [query_info["query"]],
                            "n_results": 3,
                        },
                    )

                    try:
                        results = json.loads(query_response.content[0].text)
                        print("  📋 Top matches:")
                        for j, (doc_id, document, distance, metadata) in enumerate(
                            zip(
                                results["ids"][0],
                                results["documents"][0],
                                results["distances"][0],
                                results["metadatas"][0],
                            )
                        ):
                            print(f"    {j+1}. [{doc_id}] (similarity: {1-distance:.3f})")
                            print(f"       Category: {metadata.get('category', 'N/A')}")
                            print(f"       Content: {document[:100]}...")
                    except json.JSONDecodeError:
                        print(f"  📋 Query result: {query_response.content[0].text}")

                # Step 6: Metadata filtering
                print("\n🏷️  Step 6: Metadata-based filtering...")

                # Filter by difficulty level
                filter_response = await session.call_tool(
                    "chroma_get_documents",
                    {"collection_name": collection_name, "where": {"difficulty": "intermediate"}},
                )

                try:
                    filter_results = json.loads(filter_response.content[0].text)
                    print(
                        f"  Found {len(filter_results.get('ids', []))} intermediate-level documents:"
                    )
                    for doc_id, metadata in zip(
                        filter_results.get("ids", []), filter_results.get("metadatas", [])
                    ):
                        print(f"    • {doc_id}: {metadata.get('category', 'N/A')}")
                except json.JSONDecodeError:
                    print(f"  Filter result: {filter_response.content[0].text}")

                # Step 7: Combined semantic + metadata query
                print("\n🎯 Step 7: Combined semantic search with metadata filtering...")

                combined_response = await session.call_tool(
                    "chroma_query_documents",
                    {
                        "collection_name": collection_name,
                        "query_texts": ["artificial intelligence and learning"],
                        "n_results": 5,
                        "where": {"difficulty": {"$in": ["beginner", "intermediate"]}},
                    },
                )

                try:
                    combined_results = json.loads(combined_response.content[0].text)
                    print("  🎯 AI-related documents (beginner/intermediate only):")
                    for doc_id, document, distance, metadata in zip(
                        combined_results["ids"][0],
                        combined_results["documents"][0],
                        combined_results["distances"][0],
                        combined_results["metadatas"][0],
                    ):
                        print(
                            f"    • [{doc_id}] {metadata.get('category', 'N/A')} (similarity: {1-distance:.3f})"
                        )
                except json.JSONDecodeError:
                    print(f"  🎯 Combined query result: {combined_response.content[0].text}")

                # Step 8: Peek at collection contents
                print(f"\n👀 Step 8: Peeking at collection contents...")
                peek_response = await session.call_tool(
                    "chroma_peek_collection", {"collection_name": collection_name, "limit": 3}
                )

                try:
                    peek_results = json.loads(peek_response.content[0].text)
                    print("  📄 Sample documents:")
                    for i, (doc_id, document, metadata) in enumerate(
                        zip(
                            peek_results.get("ids", []),
                            peek_results.get("documents", []),
                            peek_results.get("metadatas", []),
                        ),
                        1,
                    ):
                        print(f"    {i}. [{doc_id}] {metadata.get('category', 'N/A')}")
                        print(f"       {document[:80]}...")
                except json.JSONDecodeError:
                    print(f"  📄 Peek result: {peek_response.content[0].text}")

                print("\n" + "=" * 60)
                print("✅ ChromaDB MCP Demo completed successfully!")
                print(f"📦 Created collection: {collection_name}")
                print(f"📄 Added {len(sample_documents)} documents")
                print("🔍 Demonstrated semantic search, metadata filtering, and combined queries")
                print("=" * 60)

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
