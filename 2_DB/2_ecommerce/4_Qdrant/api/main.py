"""
Qdrant API service for AI-powered e-commerce recommendations.
Provides vector similarity search, personalized recommendations, and semantic search.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
import numpy as np
import uvicorn
import httpx
import asyncio

# Initialize FastAPI app
app = FastAPI(
    title="Qdrant E-commerce API",
    description="AI-powered product recommendations and semantic search using vector embeddings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for clients
qdrant_client = None
embedding_model = None

# MSSQL service configuration
MSSQL_API_BASE = "http://localhost:8001"

# Pydantic models
class SimilarProductsResponse(BaseModel):
    product_id: int
    similar_products: List[Dict[str, Any]]
    similarity_scores: List[float]

class RecommendationRequest(BaseModel):
    algorithm: str = "hybrid"
    limit: int = 10
    category_filter: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[Dict[str, Any]]
    algorithm_used: str

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10
    category_filter: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class SemanticSearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    similarity_scores: List[float]

class StatusResponse(BaseModel):
    status: str
    collections: Dict[str, Any]
    model_info: Dict[str, str]


async def fetch_product_details(product_id: int) -> Optional[Dict]:
    """Fetch product details from MSSQL API service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MSSQL_API_BASE}/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Product {product_id} not found in MSSQL service: {response.status_code}")
                return None
    except httpx.RequestError as e:
        print(f"Error fetching product {product_id} from MSSQL service: {e}")
        return None

async def fetch_product_thumbnail(product_id: int) -> Optional[str]:
    """Fetch product thumbnail URL from MSSQL API service."""
    product_details = await fetch_product_details(product_id)
    return product_details.get('thumbnail_url') if product_details else None


@app.on_event("startup")
async def startup_event():
    """Initialize connections and models on startup."""
    global qdrant_client, embedding_model
    
    print("🚀 Starting Qdrant API service...")
    
    # Initialize Qdrant client
    try:
        qdrant_client = QdrantClient(host="localhost", port=6333)
        print("✓ Connected to Qdrant")
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        raise
    
    # Initialize embedding model
    try:
        print("🤖 Loading SentenceTransformer model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded")
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        raise
    
    print("✅ Qdrant API service ready!")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "qdrant-api"}

@app.get("/debug/collections")
async def debug_collections():
    """Debug endpoint to check collection contents."""
    try:
        collections = qdrant_client.get_collections()
        result = {}
        
        for collection in collections.collections:
            collection_info = qdrant_client.get_collection(collection.name)
            result[collection.name] = {
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size if hasattr(collection_info.config.params, 'vectors') else "unknown"
            }
            
            # Get a few sample point IDs
            try:
                scroll_result = qdrant_client.scroll(
                    collection_name=collection.name,
                    limit=5,
                    with_payload=False,
                    with_vectors=False
                )
                sample_ids = [point.id for point in scroll_result[0]]
                result[collection.name]["sample_ids"] = sample_ids
            except:
                result[collection.name]["sample_ids"] = "failed to retrieve"
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed status of the vector database."""
    try:
        collections = qdrant_client.get_collections()
        
        product_info = qdrant_client.get_collection("product_embeddings")
        user_info = qdrant_client.get_collection("user_preference_embeddings")
        
        return StatusResponse(
            status="healthy",
            collections={
                "product_embeddings": {
                    "points_count": product_info.points_count,
                    "vector_size": product_info.config.params.vectors.size
                },
                "user_preference_embeddings": {
                    "points_count": user_info.points_count,
                    "vector_size": user_info.config.params.vectors.size
                }
            },
            model_info={
                "name": "all-MiniLM-L6-v2",
                "type": "SentenceTransformer",
                "dimension": str(len(embedding_model.encode(["test"])[0]))
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.get("/similar/{product_id}", response_model=SimilarProductsResponse)
async def get_similar_products(
    product_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Number of similar products to return"),
    category_filter: Optional[str] = Query(default=None, description="Filter by category"),
    min_price: Optional[float] = Query(default=None, description="Minimum price filter"),
    max_price: Optional[float] = Query(default=None, description="Maximum price filter")
):
    """Find products similar to the given product using vector similarity."""
    try:
        # Build filter conditions
        filter_conditions = []
        
        if category_filter:
            filter_conditions.append(
                FieldCondition(key="metadata.category", match=MatchValue(value=category_filter))
            )
        
        if min_price is not None or max_price is not None:
            price_range = Range()
            if min_price is not None:
                price_range.gte = min_price
            if max_price is not None:
                price_range.lte = max_price
            filter_conditions.append(
                FieldCondition(key="metadata.price", range=price_range)
            )
        
        # Create filter
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Get the product vector
        try:
            product_vectors = qdrant_client.retrieve(
                collection_name="product_embeddings",
                ids=[product_id],
                with_vectors=True
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve product vector: {str(e)}")
        
        if not product_vectors:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found in vector database")
        
        product_vector = product_vectors[0].vector
        if product_vector is None:
            raise HTTPException(status_code=500, detail=f"Product {product_id} has no vector data")
        
        # Search for similar products
        search_result = qdrant_client.search(
            collection_name="product_embeddings",
            query_vector=product_vector,
            query_filter=search_filter,
            limit=limit + 1  # +1 to exclude the original product
        )
        
        # Process results
        similar_products = []
        similarity_scores = []
        
        for result in search_result:
            # Skip the original product
            if int(result.id) == product_id:
                continue
            
            # Check if product exists in MSSQL and fetch details
            product_details = await fetch_product_details(int(result.id))
            if not product_details:
                # Skip products that don't exist in MSSQL
                print(f"Skipping product {result.id} - not found in MSSQL")
                continue
            
            product_data = {
                "id": int(result.id),
                "name": result.payload["metadata"]["name"],
                "category": result.payload["metadata"]["category"],
                "brand": result.payload["metadata"]["brand"],
                "price": result.payload["metadata"]["price"],
                "rating": result.payload["metadata"]["rating"],
                "in_stock": result.payload["metadata"]["in_stock"],
                "thumbnail_url": product_details.get('thumbnail_url')
            }
            
            similar_products.append(product_data)
            similarity_scores.append(float(result.score))
            
            if len(similar_products) >= limit:
                break
        
        return SimilarProductsResponse(
            product_id=product_id,
            similar_products=similar_products,
            similarity_scores=similarity_scores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find similar products: {str(e)}")


@app.post("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    user_id: int,
    request: RecommendationRequest
):
    """Get personalized product recommendations for a user."""
    try:
        # Get user's preference vector
        print(f"DEBUG: Attempting to retrieve user {user_id} from Qdrant")
        try:
            user_vectors = qdrant_client.retrieve(
                collection_name="user_preference_embeddings",
                ids=[user_id],
                with_vectors=True
            )
            print(f"DEBUG: Retrieved {len(user_vectors) if user_vectors else 0} user vectors")
        except Exception as e:
            print(f"DEBUG: Exception during user vector retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve user vector: {str(e)}")
        
        if not user_vectors:
            print(f"DEBUG: No user vectors found for user {user_id}")
            raise HTTPException(status_code=404, detail=f"User {user_id} not found in vector database")
        
        user_vector = user_vectors[0].vector
        user_payload = user_vectors[0].payload
        
        # Debug logging and validation
        print(f"DEBUG: Retrieved user vector type: {type(user_vector)}")
        print(f"DEBUG: User vector is None: {user_vector is None}")
        if user_vector is not None:
            print(f"DEBUG: User vector length: {len(user_vector) if hasattr(user_vector, '__len__') else 'No length'}")
            print(f"DEBUG: User vector first few values: {user_vector[:5] if hasattr(user_vector, '__getitem__') else 'Not indexable'}")
        
        # Strict validation before proceeding
        if user_vector is None:
            raise HTTPException(status_code=500, detail=f"User {user_id} has no vector data - vector is None")
        
        if not isinstance(user_vector, list):
            raise HTTPException(status_code=500, detail=f"User {user_id} vector is not a list - got {type(user_vector)}")
        
        if len(user_vector) == 0:
            raise HTTPException(status_code=500, detail=f"User {user_id} has empty vector data")
        
        # Build filter conditions
        filter_conditions = []
        
        # Only recommend in-stock products
        filter_conditions.append(
            FieldCondition(key="metadata.in_stock", match=MatchValue(value=True))
        )
        
        if request.category_filter:
            filter_conditions.append(
                FieldCondition(key="metadata.category", match=MatchValue(value=request.category_filter))
            )
        
        if request.min_price is not None or request.max_price is not None:
            price_range = Range()
            if request.min_price is not None:
                price_range.gte = request.min_price
            if request.max_price is not None:
                price_range.lte = request.max_price
            filter_conditions.append(
                FieldCondition(key="metadata.price", range=price_range)
            )
        
        # Algorithm-specific logic
        if request.algorithm == "category_based":
            # Recommend from user's preferred categories
            preferred_categories = user_payload.get("metadata", {}).get("preferred_categories", [])
            if preferred_categories:
                filter_conditions.append(
                    FieldCondition(key="metadata.category", match=MatchValue(value=preferred_categories[0]))
                )
        
        elif request.algorithm == "price_based":
            # Recommend products in user's price range based on history
            avg_order_value = user_payload.get("metadata", {}).get("avg_order_value", 50)
            price_range = Range(gte=avg_order_value * 0.5, lte=avg_order_value * 2)
            filter_conditions.append(
                FieldCondition(key="metadata.price", range=price_range)
            )
        
        # Create filter
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Search for recommendations
        search_result = qdrant_client.search(
            collection_name="product_embeddings",
            query_vector=user_vector,
            query_filter=search_filter,
            limit=request.limit
        )
        
        # Process results
        recommendations = []
        for result in search_result:
            # Check if product exists in MSSQL and fetch details
            product_details = await fetch_product_details(int(result.id))
            if not product_details:
                # Skip products that don't exist in MSSQL
                print(f"Skipping product {result.id} - not found in MSSQL")
                continue
            
            product_data = {
                "id": int(result.id),
                "name": result.payload["metadata"]["name"],
                "category": result.payload["metadata"]["category"],
                "brand": result.payload["metadata"]["brand"],
                "price": result.payload["metadata"]["price"],
                "rating": result.payload["metadata"]["rating"],
                "similarity_score": float(result.score),
                "recommendation_reason": _get_recommendation_reason(
                    result.payload["metadata"], user_payload, request.algorithm
                ),
                "thumbnail_url": product_details.get('thumbnail_url')
            }
            recommendations.append(product_data)
        
        return RecommendationResponse(
            user_id=user_id,
            recommendations=recommendations,
            algorithm_used=request.algorithm
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@app.post("/search/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search using natural language queries."""
    try:
        # Generate embedding for the search query
        query_embedding = embedding_model.encode([request.query])[0]
        
        # Build filter conditions
        filter_conditions = []
        
        if request.category_filter:
            filter_conditions.append(
                FieldCondition(key="metadata.category", match=MatchValue(value=request.category_filter))
            )
        
        if request.min_price is not None or request.max_price is not None:
            price_range = Range()
            if request.min_price is not None:
                price_range.gte = request.min_price
            if request.max_price is not None:
                price_range.lte = request.max_price
            filter_conditions.append(
                FieldCondition(key="metadata.price", range=price_range)
            )
        
        # Create filter
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Perform semantic search
        search_result = qdrant_client.search(
            collection_name="product_embeddings",
            query_vector=query_embedding.tolist(),
            query_filter=search_filter,
            limit=request.limit
        )
        
        # Process results
        results = []
        similarity_scores = []
        
        for result in search_result:
            # Check if product exists in MSSQL and fetch details
            product_details = await fetch_product_details(int(result.id))
            if not product_details:
                # Skip products that don't exist in MSSQL
                print(f"Skipping product {result.id} - not found in MSSQL")
                continue
            
            product_data = {
                "id": int(result.id),
                "name": result.payload["metadata"]["name"],
                "category": result.payload["metadata"]["category"],
                "brand": result.payload["metadata"]["brand"],
                "price": result.payload["metadata"]["price"],
                "rating": result.payload["metadata"]["rating"],
                "in_stock": result.payload["metadata"]["in_stock"],
                "thumbnail_url": product_details.get('thumbnail_url')
            }
            results.append(product_data)
            similarity_scores.append(float(result.score))
        
        return SemanticSearchResponse(
            query=request.query,
            results=results,
            similarity_scores=similarity_scores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform semantic search: {str(e)}")


@app.get("/collections/info")
async def get_collections_info():
    """Get information about all collections."""
    try:
        collections = qdrant_client.get_collections()
        
        collection_details = {}
        for collection in collections.collections:
            info = qdrant_client.get_collection(collection.name)
            collection_details[collection.name] = {
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value
            }
        
        return {
            "total_collections": len(collections.collections),
            "collections": collection_details
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections info: {str(e)}")


def _get_recommendation_reason(product_payload: Dict[str, Any], user_payload: Dict[str, Any], algorithm: str) -> str:
    """Generate a human-readable reason for the recommendation."""
    if algorithm == "category_based":
        return f"Recommended because you're interested in {product_payload['category']}"
    elif algorithm == "price_based":
        return f"Recommended based on your price preferences (${product_payload['price']:.2f})"
    elif algorithm == "hybrid":
        user_metadata = user_payload.get("metadata", {})
        if product_payload["category"] in user_metadata.get("preferred_categories", []):
            return f"Recommended because you like {product_payload['category']} products"
        else:
            return "Recommended based on your overall preferences"
    else:
        return "Recommended based on vector similarity"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)