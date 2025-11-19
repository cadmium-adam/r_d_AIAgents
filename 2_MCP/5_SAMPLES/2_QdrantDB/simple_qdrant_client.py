import asyncio
import json
from datetime import datetime

from mcp.client.sse import sse_client
from mcp import ClientSession


async def main():
    """
    QdrantDB MCP Client Demo
    
    Demonstrates vector database operations using Qdrant MCP server
    connecting to Docker Qdrant instance at localhost:6333
    """
    
    print("🚀 Starting QdrantDB MCP Client Demo")
    print("=" * 60)
    
    # MCP server endpoint (will be started separately)
    server_url = "http://localhost:6400"  # MCP server port
    
    try:
        async with sse_client(f"{server_url}/sse") as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                print("🔄 Initializing MCP session...")
                result = await session.initialize()
                print("✅ MCP session initialized successfully!")
                
                # Test ping
                ping_result = await session.send_ping()
                print(f"📡 Ping result: {ping_result}")
                
                # List available tools
                print("\n📋 Available QdrantDB Tools:")
                tools_list_response = await session.list_tools()
                for tool in tools_list_response.tools:
                    print(f"  • {tool.name}: {tool.description}")
                
                print("\n" + "=" * 60)
                
                # Collection name for our demo
                collection_name = f"ai_knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                print(f"📦 Using collection: '{collection_name}'")
                
                # Step 1: Store sample documents with metadata
                print("\n📄 Step 1: Storing sample AI/ML documents...")
                
                sample_documents = [
                    {
                        "information": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without explicit programming.",
                        "metadata": {
                            "category": "machine_learning",
                            "difficulty": "beginner",
                            "tags": "AI,ML,basics",
                            "author": "demo",
                            "doc_id": "doc_1"
                        }
                    },
                    {
                        "information": "Deep learning uses neural networks with multiple layers to model and understand complex patterns in large datasets, enabling breakthroughs in image recognition and natural language processing.",
                        "metadata": {
                            "category": "deep_learning", 
                            "difficulty": "intermediate",
                            "tags": "deep_learning,neural_networks,NLP",
                            "author": "demo",
                            "doc_id": "doc_2"
                        }
                    },
                    {
                        "information": "Vector databases store and retrieve high-dimensional vector embeddings, enabling semantic search and similarity matching for AI applications.",
                        "metadata": {
                            "category": "databases",
                            "difficulty": "intermediate",
                            "tags": "vectors,embeddings,search",
                            "author": "demo", 
                            "doc_id": "doc_3"
                        }
                    },
                    {
                        "information": "Large Language Models like GPT and Claude are transformer-based neural networks trained on vast amounts of text data to understand and generate human-like text.",
                        "metadata": {
                            "category": "language_models",
                            "difficulty": "advanced",
                            "tags": "LLM,transformers,GPT,Claude",
                            "author": "demo",
                            "doc_id": "doc_4"
                        }
                    },
                    {
                        "information": "Retrieval Augmented Generation (RAG) combines information retrieval with language generation, allowing AI models to access external knowledge bases.",
                        "metadata": {
                            "category": "rag",
                            "difficulty": "advanced", 
                            "tags": "RAG,retrieval,generation,knowledge",
                            "author": "demo",
                            "doc_id": "doc_5"
                        }
                    }
                ]
                
                for i, doc in enumerate(sample_documents, 1):
                    store_response = await session.call_tool("qdrant-store", {
                        "information": doc["information"],
                        "metadata": doc["metadata"],
                        "collection_name": collection_name
                    })
                    print(f"  ✅ Stored document {i}: {doc['metadata']['doc_id']}")
                
                print(f"\n📊 Stored {len(sample_documents)} documents in collection '{collection_name}'")
                
                # Step 2: Semantic search queries
                print("\n🔍 Step 2: Performing semantic search queries...")
                
                queries = [
                    {
                        "query": "How do neural networks learn from data?",
                        "description": "Query about neural network learning"
                    },
                    {
                        "query": "What are embedding vectors used for?", 
                        "description": "Query about vector embeddings"
                    },
                    {
                        "query": "How do modern AI chatbots work?",
                        "description": "Query about conversational AI"
                    },
                    {
                        "query": "What is machine learning and artificial intelligence?",
                        "description": "Query about ML and AI basics"
                    }
                ]
                
                for i, query_info in enumerate(queries, 1):
                    print(f"\n  Query {i}: {query_info['description']}")
                    print(f"  Question: '{query_info['query']}'")
                    
                    find_response = await session.call_tool("qdrant-find", {
                        "query": query_info["query"],
                        "collection_name": collection_name
                    })
                    
                    print("  📋 Results:")
                    # The response should contain the search results
                    if hasattr(find_response, 'content') and find_response.content:
                        for j, content in enumerate(find_response.content):
                            if hasattr(content, 'text'):
                                result_text = content.text
                                # Try to extract useful information from the response
                                print(f"    {j+1}. {result_text[:200]}...")
                            else:
                                print(f"    {j+1}. {str(content)[:200]}...")
                    else:
                        print(f"    Response: {str(find_response)[:200]}...")
                
                # Step 3: Test different search patterns
                print("\n🎯 Step 3: Testing specific domain searches...")
                
                domain_queries = [
                    {
                        "query": "vector embeddings and similarity search",
                        "expected": "Should find the vector database document"
                    },
                    {
                        "query": "deep neural networks and pattern recognition", 
                        "expected": "Should find the deep learning document"
                    },
                    {
                        "query": "language models and text generation",
                        "expected": "Should find the LLM document"
                    }
                ]
                
                for query_info in domain_queries:
                    print(f"\n  🔍 Searching: '{query_info['query']}'")
                    print(f"     Expected: {query_info['expected']}")
                    
                    domain_response = await session.call_tool("qdrant-find", {
                        "query": query_info["query"],
                        "collection_name": collection_name
                    })
                    
                    print("     📋 Top result:")
                    if hasattr(domain_response, 'content') and domain_response.content:
                        top_result = domain_response.content[0]
                        if hasattr(top_result, 'text'):
                            print(f"        {top_result.text[:150]}...")
                        else:
                            print(f"        {str(top_result)[:150]}...")
                    else:
                        print(f"        {str(domain_response)[:150]}...")
                
                # Step 4: Store and retrieve code snippets (demonstrate flexibility)
                print("\n💻 Step 4: Storing and retrieving code examples...")
                
                code_examples = [
                    {
                        "information": "Python function to calculate cosine similarity between two vectors using numpy",
                        "metadata": {
                            "language": "python",
                            "topic": "vector_similarity",
                            "difficulty": "intermediate",
                            "code": "import numpy as np\n\ndef cosine_similarity(a, b):\n    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))"
                        }
                    },
                    {
                        "information": "JavaScript async function to fetch data from a REST API with error handling",
                        "metadata": {
                            "language": "javascript", 
                            "topic": "api_request",
                            "difficulty": "beginner",
                            "code": "async function fetchData(url) {\n  try {\n    const response = await fetch(url);\n    return await response.json();\n  } catch (error) {\n    console.error('Fetch error:', error);\n  }\n}"
                        }
                    }
                ]
                
                for code_example in code_examples:
                    await session.call_tool("qdrant-store", {
                        "information": code_example["information"],
                        "metadata": code_example["metadata"],
                        "collection_name": collection_name
                    })
                    print(f"  ✅ Stored code example: {code_example['metadata']['language']} - {code_example['metadata']['topic']}")
                
                # Search for code examples
                code_queries = [
                    "vector similarity calculation in Python",
                    "async API request with error handling",
                    "JavaScript fetch function"
                ]
                
                print("\n  🔍 Searching for code examples:")
                for code_query in code_queries:
                    print(f"\n    Query: '{code_query}'")
                    code_response = await session.call_tool("qdrant-find", {
                        "query": code_query,
                        "collection_name": collection_name
                    })
                    
                    if hasattr(code_response, 'content') and code_response.content:
                        result = code_response.content[0]
                        if hasattr(result, 'text'):
                            print(f"    📋 Found: {result.text[:100]}...")
                        else:
                            print(f"    📋 Found: {str(result)[:100]}...")
                
                print("\n" + "=" * 60)
                print("✅ QdrantDB MCP Demo completed successfully!")
                print(f"📦 Used collection: {collection_name}")
                print(f"📄 Stored {len(sample_documents) + len(code_examples)} total documents")
                print("🔍 Demonstrated semantic search across AI/ML content and code examples")
                print("🎯 Showed flexible metadata storage and retrieval")
                print("=" * 60)
                
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())