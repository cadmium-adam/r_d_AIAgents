import os
import json
import yfinance as yf
from ollama import chat, ChatResponse, Client as OllamaClient
from openai import OpenAI
from pprint import pprint
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional, Union
from curl_cffi import requests
import pyodbc
import pymongo
from elasticsearch import Elasticsearch
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from minio import Minio
from minio.error import S3Error
import sqlalchemy
from sqlalchemy import create_engine, text
from datetime import datetime, date
from decimal import Decimal

# Load environment variables
load_dotenv()

# Custom JSON encoder for handling datetime and Decimal objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# Client configuration
AI_PROVIDER = os.environ.get("AI_PROVIDER", "ollama").lower()  # "ollama" or "openai"

# Ollama configuration
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ollama_model = os.environ.get("OLLAMA_MODEL", "mistral:latest")

# OpenAI configuration
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Initialize clients based on provider
ollama_client = None
openai_client = None

if AI_PROVIDER == "ollama":
    ollama_client = OllamaClient(host=ollama_host)
    current_model = ollama_model
    print(f"🚀 Using Ollama: {ollama_model} at {ollama_host}")
elif AI_PROVIDER == "openai":
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        current_model = openai_model
        print(f"🚀 Using OpenAI: {openai_model}")
    else:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        print("Falling back to Ollama...")
        AI_PROVIDER = "ollama"
        ollama_client = OllamaClient(host=ollama_host)
        current_model = ollama_model
else:
    print(f"❌ Unknown AI_PROVIDER: {AI_PROVIDER}. Falling back to Ollama...")
    AI_PROVIDER = "ollama"
    ollama_client = OllamaClient(host=ollama_host)
    current_model = ollama_model

# Database Configuration
DB_CONFIG = {
    "mssql": {
        "server": os.environ.get("MSSQL_SERVER", "localhost"),
        "port": os.environ.get("MSSQL_PORT", "1433"),
        "database": os.environ.get("MSSQL_DATABASE", "ECommerceDB"),
        "username": os.environ.get("MSSQL_USERNAME", "sa"),
        "password": os.environ.get("MSSQL_PASSWORD", "Heslo_1234"),
    },
    "mongodb": {
        "host": os.environ.get("MONGODB_HOST", "localhost"),
        "port": os.environ.get("MONGODB_PORT", "27017"),
        "database": os.environ.get("MONGODB_DATABASE", "ecommerce_analytics"),
        "username": os.environ.get("MONGODB_USERNAME", "admin"),
        "password": os.environ.get("MONGODB_PASSWORD", "admin123"),
    },
    "elasticsearch": {
        "host": os.environ.get("ELASTICSEARCH_HOST", "localhost"),
        "port": os.environ.get("ELASTICSEARCH_PORT", "9200"),
        "username": os.environ.get("ELASTICSEARCH_USERNAME", ""),
        "password": os.environ.get("ELASTICSEARCH_PASSWORD", ""),
    },
    "qdrant": {
        "host": os.environ.get("QDRANT_HOST", "localhost"),
        "port": os.environ.get("QDRANT_PORT", "6333"),
        "api_key": os.environ.get("QDRANT_API_KEY", ""),
    },
    "minio": {
        "endpoint": os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.environ.get("MINIO_ACCESS_KEY", "admin"),
        "secret_key": os.environ.get("MINIO_SECRET_KEY", "password123"),
        "secure": os.environ.get("MINIO_SECURE", "false").lower() == "true",
    }
}

# Database Tool Implementations

def query_mssql(query: str, description: str = "") -> Dict[str, Any]:
    """
    Execute SQL queries against the MSSQL ECommerceDB database.
    Tables: Users, Products, Orders, OrderItems, Categories, Payments.
    Example: SELECT * FROM Users WHERE FirstName LIKE '%John%'
    """
    try:
        config = DB_CONFIG["mssql"]
        # Use ODBC Driver 18 with additional connection parameters
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={config['server']},{config['port']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=no;"
        )
        
        sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={connection_string}"
        engine = create_engine(sqlalchemy_url, pool_pre_ping=True)
        
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            data = [dict(zip(columns, row)) for row in rows]
            
        return {
            "tool_used": "MSSQL Query Tool",
            "reason": "Used MSSQL for relational data queries involving structured business transactions",
            "query": query,
            "description": description,
            "results": data,
            "count": len(data)
        }
    except Exception as e:
        return {
            "tool_used": "MSSQL Query Tool",
            "error": str(e),
            "query": query,
            "description": description
        }


def query_mongodb(collection: str, query_filter: Union[Dict[str, Any], str] = None, limit: Union[int, str] = 10, description: str = "") -> Dict[str, Any]:
    """
    Query MongoDB document collections for flexible schema data.
    Handles product reviews, shopping carts, and AI recommendations.
    Collections: product_reviews, shopping_carts, recommendations.
    """
    try:
        config = DB_CONFIG["mongodb"]
        if config["username"]:
            # Use authSource=admin for authentication
            connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"
            client = pymongo.MongoClient(connection_string, authSource='admin')
        else:
            connection_string = f"mongodb://{config['host']}:{config['port']}"
            client = pymongo.MongoClient(connection_string)
        
        db = client[config["database"]]
        coll = db[collection]
        
        # Handle query_filter parameter (can be string from Ollama or dict from OpenAI)
        if query_filter is None:
            query_filter = {}
        elif isinstance(query_filter, str):
            try:
                query_filter = json.loads(query_filter)
            except json.JSONDecodeError:
                return {
                    "tool_used": "MongoDB Query Tool",
                    "error": f"Invalid JSON query filter string: {query_filter}",
                    "collection": collection,
                    "description": description
                }
        
        # Ensure query_filter is a dict
        if not isinstance(query_filter, dict):
            return {
                "tool_used": "MongoDB Query Tool",
                "error": f"Query filter must be dict or JSON string, got {type(query_filter)}",
                "collection": collection,
                "description": description
            }
        
        # Convert limit to int if it's a string (Ollama compatibility)
        if isinstance(limit, str):
            try:
                limit = int(limit)
            except ValueError:
                return {
                    "tool_used": "MongoDB Query Tool",
                    "error": f"Invalid limit value: {limit}, must be a number",
                    "collection": collection,
                    "description": description
                }
        
        results = list(coll.find(query_filter).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
            # Also handle datetime objects in MongoDB documents
            for key, value in result.items():
                if isinstance(value, (datetime, date)):
                    result[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    result[key] = float(value)
        
        client.close()
        
        return {
            "tool_used": "MongoDB Query Tool",
            "reason": "Used MongoDB for flexible document-based queries and behavioral analytics",
            "collection": collection,
            "filter": query_filter,
            "description": description,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "tool_used": "MongoDB Query Tool",
            "error": str(e),
            "collection": collection,
            "filter": query_filter,
            "description": description
        }


def search_elasticsearch(index: str, query: Union[Dict[str, Any], str] = None, size: int = 10, description: str = "") -> Dict[str, Any]:
    """
    Perform full-text search and analytics queries using Elasticsearch.
    Handles product search, user sessions, behavior tracking, and time-series analytics.
    Indices: products, search_analytics, user_sessions, user_behavior, analytics.
    """
    try:
        config = DB_CONFIG["elasticsearch"]
        # Configure Elasticsearch client with proper version compatibility
        es_config = {
            "hosts": [f"http://{config['host']}:{config['port']}"],
            "verify_certs": False,
            "ssl_show_warn": False,
        }
        
        if config["username"]:
            es = Elasticsearch(
                **es_config,
                basic_auth=(config["username"], config["password"])
            )
        else:
            es = Elasticsearch(**es_config)
        
        # Handle query parameter (can be string from Ollama or dict from OpenAI)
        if query is None:
            query = {"query": {"match_all": {}}}
        elif isinstance(query, str):
            try:
                query = json.loads(query)
            except json.JSONDecodeError:
                return {
                    "tool_used": "Elasticsearch Search Tool",
                    "error": f"Invalid JSON query string: {query}",
                    "index": index,
                    "description": description
                }
        
        # Now handle the parsed query (whether it came from string or dict)
        if isinstance(query, dict) and "query" not in query:
            # Check if it's already a valid Elasticsearch query type
            es_query_types = {"match", "term", "range", "bool", "wildcard", "prefix", "exists", "match_all", "match_phrase"}
            if any(query_type in query for query_type in es_query_types):
                # Already a valid ES query, just wrap it
                query = {"query": query}
            else:
                # Convert simple field:value pairs - use match for text, term for exact values
                if len(query) == 1:
                    field, value = next(iter(query.items()))
                    # For Ollama compatibility: use match for text fields, term for numeric/exact
                    if isinstance(value, str) and not value.isdigit():
                        query = {"query": {"match": {field: value}}}
                    else:
                        query = {"query": {"term": {field: value}}}
                else:
                    query = {"query": {"match": query}}
        
        # Include size in the query body to avoid deprecation warning
        if isinstance(query, dict):
            # Convert size to int if it's a string (Ollama compatibility)
            if isinstance(size, str):
                try:
                    size = int(size)
                except ValueError:
                    size = 10  # Default fallback
            query["size"] = size
        else:
            return {
                "tool_used": "Elasticsearch Search Tool", 
                "error": f"Query must be dict or JSON string, got {type(query)}",
                "index": index,
                "description": description
            }
        
        response = es.search(index=index, body=query)
        
        hits = response["hits"]["hits"]
        results = [hit["_source"] for hit in hits]
        
        return {
            "tool_used": "Elasticsearch Search Tool",
            "reason": "Used Elasticsearch for full-text search and real-time analytics",
            "index": index,
            "query": query,
            "description": description,
            "results": results,
            "total_hits": response["hits"]["total"]["value"],
            "max_score": response["hits"]["max_score"]
        }
    except Exception as e:
        return {
            "tool_used": "Elasticsearch Search Tool",
            "error": str(e),
            "index": index,
            "query": query,
            "description": description
        }


def search_qdrant(collection_name: str, query_vector: List[float] = None, limit: int = 5, score_threshold: float = 0.0, description: str = "") -> Dict[str, Any]:
    """
    Perform semantic similarity searches using vector embeddings in Qdrant.
    Handles product similarity, personalized recommendations, and semantic search.
    IMPORTANT: Vector must be exactly 384 dimensions. If not provided, uses a default vector.
    """
    try:
        config = DB_CONFIG["qdrant"]
        
        # Validate or create vector
        if query_vector is None:
            # Create a default vector for demonstration
            import random
            random.seed(42)  # For reproducibility
            query_vector = [random.random() for _ in range(384)]
            description += " (Using default vector)"
        elif len(query_vector) != 384:
            return {
                "tool_used": "Qdrant Vector Search Tool",
                "error": f"Vector dimension mismatch: expected 384 dimensions, got {len(query_vector)}. Please provide exactly 384 float values.",
                "collection": collection_name,
                "description": description,
                "hint": "In a real system, vectors would be generated by an embedding model like all-MiniLM-L6-v2"
            }
        
        if config["api_key"]:
            client = QdrantClient(
                host=config["host"],
                port=int(config["port"]),
                api_key=config["api_key"]
            )
        else:
            client = QdrantClient(host=config["host"], port=int(config["port"]))
        
        # Use query_points method (recommended)
        search_result = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        # Extract points from query_points response
        if hasattr(search_result, 'points'):
            points = search_result.points
        else:
            points = search_result
        
        results = []
        for point in points:
            results.append({
                "id": point.id,
                "score": point.score,
                "payload": point.payload
            })
        
        # If using default vector, try to find relevant products by category/content
        if "default vector" in description and ("tennis" in description.lower() or "sport" in description.lower()):
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue
            
            # First try to get sports products and filter for tennis-related ones
            try:
                # Search for sports category products
                sports_results = client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="metadata.category",
                                match=MatchValue(value="Sports")
                            )
                        ]
                    ),
                    limit=50  # Get all sports products to filter
                )
                
                if hasattr(sports_results, 'points') and sports_results.points:
                    # Filter for tennis-related products if tennis is mentioned
                    if "tennis" in description.lower():
                        tennis_products = []
                        other_sports = []
                        
                        for point in sports_results.points:
                            content = point.payload.get('content', '').lower()
                            name = point.payload.get('metadata', {}).get('name', '').lower()
                            
                            if 'tennis' in content or 'tennis' in name:
                                tennis_products.append(point)
                            else:
                                other_sports.append(point)
                        
                        # Prefer tennis products, fallback to other sports
                        filtered_points = tennis_products[:limit] if tennis_products else other_sports[:limit]
                        
                        if filtered_points:
                            results = []
                            for point in filtered_points:
                                results.append({
                                    "id": point.id,
                                    "score": point.score,
                                    "payload": point.payload
                                })
                            
                            filter_type = "tennis-specific" if tennis_products else "sports"
                            description += f" (Found {filter_type} products using category filter)"
                    else:
                        # Just return sports products
                        results = []
                        for point in sports_results.points[:limit]:
                            results.append({
                                "id": point.id,
                                "score": point.score,
                                "payload": point.payload
                            })
                        description += " (Found sports products using category filter)"
                    
            except Exception as filter_error:
                # Continue with original results if filter fails
                pass
        
        return {
            "tool_used": "Qdrant Vector Search Tool",
            "reason": "Used Qdrant for semantic similarity search and AI-powered recommendations",
            "collection": collection_name,
            "description": description,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "tool_used": "Qdrant Vector Search Tool",
            "error": str(e),
            "collection": collection_name,
            "description": description
        }


def access_minio(bucket_name: str, object_name: str = None, list_objects: bool = False, description: str = "") -> Dict[str, Any]:
    """
    Access and manage files and media stored in MinIO object storage.
    Handles product images, user uploads, reports, and file metadata.
    """
    try:
        config = DB_CONFIG["minio"]
        client = Minio(
            config["endpoint"],
            access_key=config["access_key"],
            secret_key=config["secret_key"],
            secure=config["secure"]
        )
        
        if list_objects:
            objects = client.list_objects(bucket_name, recursive=True)
            results = []
            for obj in objects:
                results.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag
                })
            
            return {
                "tool_used": "MinIO Object Storage Tool",
                "reason": "Used MinIO for object storage and file metadata operations",
                "bucket": bucket_name,
                "operation": "list_objects",
                "description": description,
                "results": results,
                "count": len(results)
            }
        
        elif object_name:
            stat = client.stat_object(bucket_name, object_name)
            presigned_url = client.presigned_get_object(bucket_name, object_name)
            
            return {
                "tool_used": "MinIO Object Storage Tool",
                "reason": "Used MinIO for file access and retrieval",
                "bucket": bucket_name,
                "object": object_name,
                "operation": "get_object_info",
                "description": description,
                "result": {
                    "size": stat.size,
                    "last_modified": stat.last_modified.isoformat(),
                    "content_type": stat.content_type,
                    "presigned_url": presigned_url
                }
            }
        
        else:
            buckets = client.list_buckets()
            results = [{"name": bucket.name, "creation_date": bucket.creation_date.isoformat()} for bucket in buckets]
            
            return {
                "tool_used": "MinIO Object Storage Tool",
                "reason": "Used MinIO for bucket listing and storage overview",
                "operation": "list_buckets",
                "description": description,
                "results": results,
                "count": len(results)
            }
            
    except Exception as e:
        return {
            "tool_used": "MinIO Object Storage Tool",
            "error": str(e),
            "bucket": bucket_name,
            "object": object_name,
            "description": description
        }

# Define custom tools (format depends on provider)
def get_tools_for_provider(provider: str):
    """Get tools in the appropriate format for the AI provider."""
    
    if provider == "ollama":
        # Ollama supports direct function references
        return [
            query_mssql,
            query_mongodb,
            search_elasticsearch,
            search_qdrant,
            access_minio
        ]
    
    elif provider == "openai":
        # OpenAI requires the structured format
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_mssql",
                    "description": "Execute SQL queries against the MSSQL ECommerceDB database. Tables: Users, Products, Orders, OrderItems, Categories, Payments. Use for structured business data and relational queries.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute (e.g., 'SELECT * FROM Users WHERE FirstName LIKE '%John%')"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what you're trying to find"
                            }
                        },
                        "required": ["query"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_mongodb",
                    "description": "Query MongoDB document collections for flexible schema data. Use for product reviews, shopping carts, and AI recommendations. Collections: product_reviews, shopping_carts, recommendations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "collection": {
                                "type": "string",
                                "description": "Collection name (e.g., 'user_sessions', 'product_reviews', 'shopping_carts')"
                            },
                            "query_filter": {
                                "type": ["object", "string"],
                                "description": "MongoDB query filter as object or JSON string (e.g., {'user_id': '12345'} or '{\"rating\": {\"$gte\": 4}}')"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of documents to return (default: 10)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what you're trying to find"
                            }
                        },
                        "required": ["collection"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_elasticsearch",
                    "description": "Perform full-text search and analytics queries using Elasticsearch. Use for product search, user sessions, behavior tracking, and time-series analytics. Indices: products, search_analytics, user_sessions, user_behavior, analytics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "Elasticsearch index name (e.g., 'products', 'search_analytics')"
                            },
                            "query": {
                                "type": ["object", "string"],
                                "description": "Elasticsearch query DSL as object or JSON string (e.g., {'match': {'name': 'iPhone'}} or '{\"range\": {\"price\": {\"gte\": 100}}}'). If not provided, returns all documents."
                            },
                            "size": {
                                "type": "integer",
                                "description": "Number of results to return (default: 10)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what you're searching for"
                            }
                        },
                        "required": ["index"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_qdrant",
                    "description": "Perform semantic similarity searches using vector embeddings in Qdrant. Use for finding similar products, personalized recommendations, and semantic search based on content similarity.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Qdrant collection name (e.g., 'product_embeddings', 'user_preferences')"
                            },
                            "query_vector": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Query vector for similarity search (must be exactly 384 floats). If not provided, uses a default vector."
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of similar items to return (default: 5)"
                            },
                            "score_threshold": {
                                "type": "number",
                                "description": "Minimum similarity score threshold (default: 0.0 for demo)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what you're looking for"
                            }
                        },
                        "required": ["collection_name"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "access_minio",
                    "description": "Access and manage files and media stored in MinIO object storage. Use for retrieving product images, user uploads, reports, and file metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "bucket_name": {
                                "type": "string",
                                "description": "MinIO bucket name (e.g., 'product-images', 'user-uploads')"
                            },
                            "object_name": {
                                "type": "string",
                                "description": "Specific object/file name to retrieve (optional)"
                            },
                            "list_objects": {
                                "type": "boolean",
                                "description": "Set to true to list all objects in the bucket"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of what you're accessing"
                            }
                        },
                        "required": ["bucket_name"],
                    },
                }
            }
        ]
    
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

# Get tools for current provider
tools = get_tools_for_provider(AI_PROVIDER)

available_functions = {
    "query_mssql": query_mssql,
    "query_mongodb": query_mongodb,
    "search_elasticsearch": search_elasticsearch,
    "search_qdrant": search_qdrant,
    "access_minio": access_minio,
}


class ReactAgent:
    """A ReAct (Reason and Act) agent that handles multiple tool calls using either Ollama or OpenAI."""
    
    def __init__(self, model: str = None, provider: str = None):
        self.provider = provider or AI_PROVIDER
        self.model = model or current_model
        self.max_iterations = 10  # Prevent infinite loops
        
    def run(self, messages: List[Dict[str, Any]]) -> str:
        """
        Run the ReAct loop until we get a final answer using the configured provider.
        
        The agent will:
        1. Call the LLM via the configured provider (Ollama or OpenAI)
        2. If tool calls are returned, execute them
        3. Add results to conversation and repeat
        4. Continue until LLM returns only text (no tool calls)
        """
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            try:
                if self.provider == "ollama":
                    response = self._call_ollama(messages)
                elif self.provider == "openai":
                    response = self._call_openai(messages)
                else:
                    return f"Error: Unsupported provider: {self.provider}"
                
                # Handle tool calls (format is different between providers)
                tool_calls = self._extract_tool_calls(response)
                
                if tool_calls:
                    # Add the assistant's message to history
                    self._add_assistant_message(messages, response)
                    
                    # Process ALL tool calls
                    for tool_call in tool_calls:
                        function_name, function_args, tool_id = self._extract_tool_call_info(tool_call)
                        
                        print(f"Executing tool: {function_name}({function_args})")
                        
                        # Call the function
                        if function_name in available_functions:
                            function_to_call = available_functions[function_name]
                            function_response = function_to_call(**function_args)
                        else:
                            function_response = {"error": f"Function {function_name} not found"}
                        
                        print(f"Tool result: {function_response}")
                        
                        # Add tool response to messages (format depends on provider)
                        self._add_tool_response(messages, function_name, function_response, tool_id)
                    
                    # Continue the loop to get the next response
                    continue
                    
                else:
                    # No tool calls - we have our final answer
                    final_content = self._extract_final_content(response)
                    
                    # Add the final assistant message to history
                    messages.append({
                        "role": "assistant",
                        "content": final_content
                    })
                    
                    print(f"\nFinal answer: {final_content}")
                    return final_content
                    
            except Exception as e:
                error_msg = f"Error calling {self.provider}: {str(e)}"
                print(error_msg)
                return error_msg
        
        # If we hit max iterations, return an error
        return "Error: Maximum iterations reached without getting a final answer."
    
    def _call_ollama(self, messages):
        """Call Ollama API."""
        return ollama_client.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )
    
    def _call_openai(self, messages):
        """Call OpenAI API."""
        return openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False
        )
    
    def _extract_tool_calls(self, response):
        """Extract tool calls from response (provider-specific format)."""
        if self.provider == "ollama":
            return response.message.tool_calls
        elif self.provider == "openai":
            return response.choices[0].message.tool_calls
        return None
    
    def _extract_tool_call_info(self, tool_call):
        """Extract tool call information (provider-specific format)."""
        if self.provider == "ollama":
            return (
                tool_call.function.name,
                tool_call.function.arguments,
                getattr(tool_call, 'id', None)
            )
        elif self.provider == "openai":
            return (
                tool_call.function.name,
                json.loads(tool_call.function.arguments),
                tool_call.id
            )
    
    def _add_assistant_message(self, messages, response):
        """Add assistant message to conversation history."""
        if self.provider == "ollama":
            messages.append(response.message)
        elif self.provider == "openai":
            response_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in response_message.tool_calls
                ]
            })
    
    def _add_tool_response(self, messages, function_name, function_response, tool_id):
        """Add tool response to conversation history."""
        if self.provider == "ollama":
            messages.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_response, cls=DateTimeEncoder),
            })
        elif self.provider == "openai":
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "name": function_name,
                "content": json.dumps(function_response, cls=DateTimeEncoder),
            })
    
    def _extract_final_content(self, response):
        """Extract final content from response."""
        if self.provider == "ollama":
            return response.message.content
        elif self.provider == "openai":
            return response.choices[0].message.content


def main():
    # Create a ReAct agent
    agent = ReactAgent()
    
    # Enhanced system prompt for educational database agent
    system_prompt = """You are an educational AI agent designed to demonstrate how different database technologies work as tools in AI systems. 

Available Database Tools:
1. MSSQL (query_mssql) - For relational data, structured business transactions
2. MongoDB (query_mongodb) - For flexible document-based data, product reviews, shopping carts, AI recommendations
3. Elasticsearch (search_elasticsearch) - For full-text search, time-series data, user sessions, behavior analytics
4. Qdrant (search_qdrant) - For vector similarity search and AI recommendations
5. MinIO (access_minio) - For object storage and file management

DATABASE SCHEMAS:

MSSQL (ECommerceDB):
- Users: Id, Email, FirstName, LastName, Phone, DateOfBirth, Street, City, State, ZipCode, Country, TotalOrders, TotalSpent, NewsletterOptIn, SMSNotifications, IsActive, JoinDate, LastLogin
- Products: Id, Name, Description, CategoryId, Price, StockQuantity, Brand, SKU, Weight, Length, Width, Height, Rating, ReviewCount, MainImageUrl, ThumbnailUrl, Features, IsActive, CreatedAt, UpdatedAt
- Orders: Id, UserId, OrderDate, Status, Subtotal, ShippingCost, TaxAmount, TotalAmount, ShippingStreet, ShippingCity, ShippingState, ShippingZipCode, ShippingCountry, PaymentMethod, TrackingNumber
- OrderItems: Id, OrderId, ProductId, ProductName, Quantity, UnitPrice, TotalPrice
- Categories: Id, Name, Description, CreatedAt
- Payments: Id, OrderId, PaymentMethod, Amount, Status, TransactionId, ProcessedAt

MongoDB (ecommerce_analytics):
- product_reviews: product_id, product_name, user_id, user_name, rating, title, comment, pros[], cons[], helpful_votes, verified_purchase, created_at
- shopping_carts: user_id, items[], total_items, subtotal, estimated_tax, estimated_shipping, estimated_total, created_at, updated_at
- recommendations: user_id, algorithm, products[], page_type, user_segment, created_at

Elasticsearch Indices:
- products: id, name, description, category, brand, price, stock_quantity, rating, review_count, tags[]
- search_analytics: timestamp, query, user_id, session_id, results_count, clicked_product_id
- popular_searches: query, search_count, last_searched, trending_score, category, suggestions[]
- user_sessions: session_id, user_id, start_time, end_time, duration_minutes, pages_viewed[], device_info, location, is_active
- user_behavior: user_id, session_id, event_type, timestamp, page_url, product_id, search_query, filters, order_total
- analytics: date, metric_type, unique_visitors, page_views, sessions, conversion_rate, revenue, top_products[], device_breakdown

Qdrant Collections:
- product_embeddings: Vector embeddings (384 dims) with metadata (id, name, description, category, brand, price, rating)
- user_preference_embeddings: Vector embeddings for personalized recommendations
NOTE: For Qdrant searches, you don't need to provide a vector - it will use a default one for demonstration. In production, vectors would be generated by an embedding model.

MinIO Buckets:
- product-images: Product photos organized by product_id
- user-uploads: User-generated content like review photos
- reports: Generated reports and exports

KEY DATA FLOWS:
- User sessions and behavior tracking → Elasticsearch (for time-series analysis)
- Product reviews and shopping carts → MongoDB (for flexible schemas)
- Business transactions → MSSQL (for ACID compliance)
- Semantic search → Qdrant (for AI/ML features)

IMPORTANT: Always explain WHY you selected each database tool and what makes it suitable for the specific query. This helps students understand the decision-making process for tool selection in AI agents.

When responding:
1. Explain your tool selection reasoning
2. Show how different databases complement each other
3. Highlight the unique strengths of each database technology
4. Provide educational context about the query patterns"""
    
    # Welcome message
    print("🎓 Educational Database Tools AI Agent")
    print("=" * 50)
    print(f"AI Provider: {AI_PROVIDER.upper()}")
    print(f"Model: {current_model}")
    if AI_PROVIDER == "ollama":
        print(f"Host: {ollama_host}")
    elif AI_PROVIDER == "openai":
        print("API: OpenAI")
    print("=" * 50)
    print("\nThis AI agent demonstrates how different database technologies work as tools.")
    print("Ask questions about data and see how the agent selects appropriate databases!")
    print("\nDatabase specializations:")
    print("- MSSQL: Users, orders, products (transactional data)")
    print("- MongoDB: Reviews, shopping carts, recommendations")
    print("- Elasticsearch: Search, sessions, behavior tracking, analytics")
    print("- Qdrant: Semantic search, AI-powered similarities")
    print("- MinIO: Files, images, documents")
    print("\nType 'help' for example queries, 'quit' to exit.")
    print("\n" + "=" * 50)
    
    # Interactive chat loop
    conversation_history = [{"role": "system", "content": system_prompt}]
    
    while True:
        try:
            user_input = input("\n🤔 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for using the Educational Database Tools AI Agent!")
                break
            
            if user_input.lower() in ['help', 'h']:
                print("\n📚 Example Queries:")
                print("1. 'Show me details about user John Doe and his purchase behavior'")
                print("2. 'Find products similar to iPhone 15 and explain the recommendations'")
                print("3. 'What are customers searching for most this month?'")
                print("4. 'Show me product images for top-rated electronics'")
                print("5. 'How many orders were placed last month?'")
                print("6. 'Find all products with ratings above 4 stars'")
                print("7. 'Show me user session data for David Jones'")
                print("8. 'What files are stored in the product-images bucket?'")
                print("9. 'Show me shopping cart for user ID 1'")
                print("10. 'Get product reviews for iPhone 15'")
                print("\nFor more examples, check the README.md file!")
                continue
            
            if not user_input:
                continue
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            print("\n🤖 Agent is thinking and selecting tools...")
            
            # Get response from agent
            result = agent.run(conversation_history.copy())
            
            # Add assistant response to conversation history
            conversation_history.append({"role": "assistant", "content": result})
            
            print(f"\n💡 {result}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using the Educational Database Tools AI Agent!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")


if __name__ == "__main__":
    main()