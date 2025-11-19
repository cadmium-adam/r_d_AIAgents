"""
Elasticsearch FastAPI service for e-commerce search and discovery.
Handles product search, autocomplete, faceted search, and search analytics.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import uvicorn
from elasticsearch import Elasticsearch
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce Elasticsearch API",
    description="Search and discovery API using Elasticsearch",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch connection
es = Elasticsearch(['http://localhost:9200'], request_timeout=60)

# Pydantic models
class SearchResult(BaseModel):
    id: int
    name: str
    description: str
    category: str
    brand: str
    price: float
    rating: Optional[float]
    review_count: int
    stock_quantity: int
    score: float
    main_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    total_hits: int
    took: int
    results: List[SearchResult]
    aggregations: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class AutocompleteResponse(BaseModel):
    suggestions: List[str]
    products: List[Dict[str, Any]]

class SearchAnalytics(BaseModel):
    query: str
    results_count: int
    user_id: Optional[int] = None
    clicked_product_id: Optional[int] = None
    clicked_position: Optional[int] = None
    filters_applied: Optional[Dict[str, Any]] = None

class PopularSearch(BaseModel):
    query: str
    search_count: int
    trending_score: float
    suggestions: List[str]

class ProductIndex(BaseModel):
    id: int
    name: str
    description: str
    category: str
    brand: str
    price: float
    stock_quantity: int
    rating: Optional[float] = None
    review_count: int = 0
    is_active: bool = True

# Helper functions
def wait_for_elasticsearch(max_retries=30):
    """Wait for Elasticsearch to be ready."""
    for i in range(max_retries):
        try:
            if es.ping():
                logger.info("Elasticsearch is ready!")
                return True
            logger.info(f"Waiting for Elasticsearch... (attempt {i+1}/{max_retries})")
            import time
            time.sleep(2)
        except Exception as e:
            logger.error(f"Elasticsearch not ready: {e}")
            import time
            time.sleep(2)
    
    raise Exception("Elasticsearch is not available after waiting")

def build_search_query(
    query: str,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock: bool = True
) -> Dict[str, Any]:
    """Build Elasticsearch query with filters."""
    
    must_clauses = []
    filter_clauses = []
    
    # Main search query
    if query:
        must_clauses.append({
            "multi_match": {
                "query": query,
                "fields": [
                    "name^3",
                    "name.autocomplete^2", 
                    "brand^2",
                    "category^1.5",
                    "description^1",
                    "tags^1.5"
                ],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "operator": "or"
            }
        })
    else:
        must_clauses.append({"match_all": {}})
    
    # Filters
    if category:
        filter_clauses.append({"term": {"category": category}})
    
    if brand:
        filter_clauses.append({"term": {"brand": brand}})
    
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        filter_clauses.append({"range": {"price": price_range}})
    
    if min_rating is not None:
        filter_clauses.append({"range": {"rating": {"gte": min_rating}}})
    
    if in_stock:
        filter_clauses.append({"range": {"stock_quantity": {"gt": 0}}})
    
    # Always filter for active products
    filter_clauses.append({"term": {"is_active": True}})
    
    search_body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
            {"rating": {"order": "desc"}},
            {"review_count": {"order": "desc"}}
        ]
    }
    
    return search_body

def track_search_analytics(
    query: str,
    results_count: int,
    user_id: Optional[int] = None,
    search_time_ms: int = 0,
    filters_applied: Optional[Dict] = None
):
    """Track search analytics in background."""
    try:
        analytics_doc = {
            "timestamp": datetime.now(),
            "query": query,
            "results_count": results_count,
            "search_time_ms": search_time_ms,
            "device_type": "web",
            "converted": False
        }
        
        if user_id:
            analytics_doc["user_id"] = user_id
            analytics_doc["session_id"] = f"sess_{user_id}_current"
        
        if filters_applied:
            analytics_doc["filters_applied"] = [
                {"name": k, "value": v} for k, v in filters_applied.items()
            ]
        
        es.index(index="search_analytics", document=analytics_doc)
        
        # Update popular searches
        if query and query.strip():
            update_popular_search(query.strip().lower())
            
    except Exception as e:
        logger.error(f"Error tracking search analytics: {e}")

def update_popular_search(query: str):
    """Update popular search count for a query."""
    try:
        # Check if the query already exists in popular searches
        search_body = {
            "query": {"match": {"query": query}},
            "size": 1
        }
        
        existing = es.search(index="popular_searches", body=search_body)
        
        if existing["hits"]["total"]["value"] > 0:
            # Update existing popular search
            doc_id = existing["hits"]["hits"][0]["_id"]
            current_doc = existing["hits"]["hits"][0]["_source"]
            
            update_body = {
                "doc": {
                    "search_count": current_doc["search_count"] + 1,
                    "last_searched": datetime.now().isoformat(),
                    "trending_score": current_doc["search_count"] + 1  # Simple trending score
                }
            }
            
            es.update(index="popular_searches", id=doc_id, body=update_body)
        else:
            # Create new popular search entry
            new_doc = {
                "query": query,
                "search_count": 1,
                "last_searched": datetime.now().isoformat(),
                "trending_score": 1.0,
                "category": "general",
                "suggestions": [
                    f"{query} sale",
                    f"{query} review",
                    f"best {query}"
                ]
            }
            
            es.index(index="popular_searches", document=new_doc)
            
    except Exception as e:
        logger.error(f"Error updating popular search: {e}")

# API Routes

@app.get("/analytics/stats")
async def get_analytics_stats():
    """Get real-time analytics statistics."""
    try:
        # Get search analytics count
        search_count_response = es.count(index="search_analytics")
        search_events_count = search_count_response["count"]
        
        # Get popular searches count  
        popular_count_response = es.count(index="popular_searches")
        popular_searches_count = popular_count_response["count"]
        
        return {
            "search_events": search_events_count,
            "popular_searches": popular_searches_count,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get analytics stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics stats")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if es.ping():
            return {"status": "healthy", "elasticsearch": "connected"}
        else:
            raise HTTPException(status_code=503, detail="Elasticsearch not available")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Elasticsearch connection failed")

@app.get("/search", response_model=SearchResponse)
async def search_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=1, le=5),
    in_stock: bool = True,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    include_aggregations: bool = False,
    user_id: Optional[int] = None,
    background_tasks: BackgroundTasks = None
):
    """Search products with filtering and faceted search."""
    try:
        # Build search query
        search_body = build_search_query(
            query=q,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            in_stock=in_stock
        )
        
        # Add pagination
        from_param = (page - 1) * size
        search_body["from"] = from_param
        search_body["size"] = size
        
        # Add aggregations for faceted search
        if include_aggregations:
            search_body["aggs"] = {
                "categories": {
                    "terms": {"field": "category", "size": 10}
                },
                "brands": {
                    "terms": {"field": "brand", "size": 10}
                },
                "price_ranges": {
                    "range": {
                        "field": "price",
                        "ranges": [
                            {"to": 25, "key": "Under $25"},
                            {"from": 25, "to": 50, "key": "$25-$50"},
                            {"from": 50, "to": 100, "key": "$50-$100"},
                            {"from": 100, "to": 250, "key": "$100-$250"},
                            {"from": 250, "key": "Over $250"}
                        ]
                    }
                },
                "ratings": {
                    "range": {
                        "field": "rating",
                        "ranges": [
                            {"from": 4, "key": "4+ stars"},
                            {"from": 3, "to": 4, "key": "3-4 stars"},
                            {"to": 3, "key": "Under 3 stars"}
                        ]
                    }
                }
            }
        
        # Execute search
        start_time = datetime.now()
        response = es.search(index="products", body=search_body)
        search_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Parse results
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            # Extract image URLs from nested images object
            images = source.get("images", {})
            main_image_url = images.get("main_image") if isinstance(images, dict) else None
            thumbnail_url = images.get("thumbnail") if isinstance(images, dict) else None
            
            results.append(SearchResult(
                id=source["id"],
                name=source["name"],
                description=source["description"],
                category=source["category"],
                brand=source["brand"],
                price=source["price"],
                rating=source.get("rating"),
                review_count=source["review_count"],
                stock_quantity=source["stock_quantity"],
                score=hit["_score"],
                main_image_url=main_image_url,
                thumbnail_url=thumbnail_url
            ))
        
        # Parse aggregations
        aggregations = None
        if include_aggregations and "aggregations" in response:
            aggregations = {}
            for agg_name, agg_data in response["aggregations"].items():
                if "buckets" in agg_data:
                    aggregations[agg_name] = [
                        {"key": bucket["key"], "count": bucket["doc_count"]}
                        for bucket in agg_data["buckets"]
                    ]
        
        # Get suggestions for empty results
        suggestions = None
        if response["hits"]["total"]["value"] == 0:
            suggestions = await get_search_suggestions(q)
        
        # Track analytics in background
        if background_tasks:
            filters_applied = {}
            if category: filters_applied["category"] = category
            if brand: filters_applied["brand"] = brand
            if min_price: filters_applied["min_price"] = min_price
            if max_price: filters_applied["max_price"] = max_price
            if min_rating: filters_applied["min_rating"] = min_rating
            
            background_tasks.add_task(
                track_search_analytics,
                q or "",
                response["hits"]["total"]["value"],
                user_id,
                search_time_ms,
                filters_applied if filters_applied else None
            )
        
        return SearchResponse(
            query=q or "",
            total_hits=response["hits"]["total"]["value"],
            took=response["took"],
            results=results,
            aggregations=aggregations,
            suggestions=suggestions
        )
    
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

async def get_search_suggestions(query: str) -> List[str]:
    """Get search suggestions for empty results."""
    try:
        # Simple suggestion based on popular searches
        suggest_body = {
            "suggest": {
                "product_suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "suggest",
                        "size": 5
                    }
                },
                "text_suggest": {
                    "text": query,
                    "term": {
                        "field": "name",
                        "size": 3
                    }
                }
            }
        }
        
        response = es.search(index="products", body=suggest_body)
        suggestions = []
        
        # Extract completion suggestions
        for suggestion in response["suggest"]["product_suggest"]:
            for option in suggestion["options"]:
                suggestions.append(option["text"])
        
        # Extract term suggestions
        for suggestion in response["suggest"]["text_suggest"]:
            for option in suggestion["options"]:
                suggestions.append(option["text"])
        
        return list(set(suggestions))[:5]  # Remove duplicates and limit to 5
    
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        return []

@app.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(
    q: str = Query(..., min_length=1, description="Search query prefix"),
    size: int = Query(5, ge=1, le=10)
):
    """Get autocomplete suggestions."""
    try:
        # Completion suggester for product names
        suggest_body = {
            "suggest": {
                "product_suggest": {
                    "prefix": q,
                    "completion": {
                        "field": "suggest",
                        "size": size,
                        "contexts": {}
                    }
                }
            }
        }
        
        response = es.search(index="products", body=suggest_body)
        
        suggestions = []
        products = []
        
        for suggestion in response["suggest"]["product_suggest"]:
            for option in suggestion["options"]:
                suggestions.append(option["text"])
                if "_source" in option:
                    source = option["_source"]
                    products.append({
                        "id": source["id"],
                        "name": source["name"],
                        "price": source["price"],
                        "category": source["category"]
                    })
        
        # If no completion suggestions, try a simple match query
        if not suggestions:
            match_body = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"name.autocomplete": {"query": q, "boost": 3}}},
                            {"match": {"brand": {"query": q, "boost": 2}}},
                            {"match": {"category": {"query": q, "boost": 1}}}
                        ]
                    }
                },
                "size": size,
                "_source": ["id", "name", "price", "category"]
            }
            
            match_response = es.search(index="products", body=match_body)
            
            for hit in match_response["hits"]["hits"]:
                source = hit["_source"]
                suggestions.append(source["name"])
                products.append({
                    "id": source["id"],
                    "name": source["name"],
                    "price": source["price"],
                    "category": source["category"]
                })
        
        return AutocompleteResponse(
            suggestions=list(set(suggestions))[:size],
            products=products[:size]
        )
    
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {e}")
        raise HTTPException(status_code=500, detail="Autocomplete failed")

@app.post("/analytics/search")
async def track_search_click(analytics: SearchAnalytics):
    """Track search result click."""
    try:
        # Update the search analytics record with click information
        update_body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"query.keyword": analytics.query}},
                        {"range": {"timestamp": {"gte": "now-1h"}}}
                    ]
                }
            },
            "script": {
                "source": """
                if (params.clicked_product_id != null) {
                    ctx._source.clicked_product_id = params.clicked_product_id;
                }
                if (params.clicked_position != null) {
                    ctx._source.clicked_position = params.clicked_position;
                }
                ctx._source.converted = true;
                """,
                "params": {
                    "clicked_product_id": analytics.clicked_product_id,
                    "clicked_position": analytics.clicked_position
                }
            }
        }
        
        if analytics.user_id:
            update_body["query"]["bool"]["must"].append({"term": {"user_id": analytics.user_id}})
        
        es.update_by_query(index="search_analytics", body=update_body)
        
        return {"message": "Search click tracked successfully"}
    
    except Exception as e:
        logger.error(f"Error tracking search click: {e}")
        raise HTTPException(status_code=500, detail="Failed to track search click")

@app.get("/analytics/popular-searches", response_model=List[PopularSearch])
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50),
    time_range: str = Query("7d", regex="^(1h|24h|7d|30d)$")
):
    """Get popular search queries."""
    try:
        # Convert time range to datetime
        time_map = {
            "1h": datetime.now() - timedelta(hours=1),
            "24h": datetime.now() - timedelta(days=1),
            "7d": datetime.now() - timedelta(days=7),
            "30d": datetime.now() - timedelta(days=30)
        }
        
        since_time = time_map[time_range]
        
        # Aggregate search queries
        agg_body = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": since_time.isoformat()}}},
                        {"exists": {"field": "query"}}
                    ]
                }
            },
            "size": 0,
            "aggs": {
                "popular_queries": {
                    "terms": {
                        "field": "query.keyword",
                        "size": limit,
                        "order": {"_count": "desc"}
                    },
                    "aggs": {
                        "unique_users": {
                            "cardinality": {"field": "user_id"}
                        },
                        "avg_results": {
                            "avg": {"field": "results_count"}
                        },
                        "conversion_rate": {
                            "filter": {"term": {"converted": True}},
                            "aggs": {
                                "rate": {
                                    "bucket_script": {
                                        "buckets_path": {
                                            "converted": "_count",
                                            "total": "_parent>_count"
                                        },
                                        "script": "params.converted / params.total"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        response = es.search(index="search_analytics", body=agg_body)
        
        popular_searches = []
        for bucket in response["aggregations"]["popular_queries"]["buckets"]:
            query = bucket["key"]
            search_count = bucket["doc_count"]
            unique_users = bucket["unique_users"]["value"]
            
            # Calculate trending score (searches * unique users)
            trending_score = search_count * unique_users
            
            # Get related suggestions
            suggestions = [
                f"{query} review",
                f"best {query}",
                f"{query} sale"
            ]
            
            popular_searches.append(PopularSearch(
                query=query,
                search_count=search_count,
                trending_score=trending_score,
                suggestions=suggestions[:3]
            ))
        
        return popular_searches
    
    except Exception as e:
        logger.error(f"Error getting popular searches: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular searches")

@app.post("/products/index")
async def index_product(product: ProductIndex):
    """Index a new product or update existing one."""
    try:
        # Prepare document for indexing
        doc = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "brand": product.brand,
            "price": product.price,
            "stock_quantity": product.stock_quantity,
            "rating": product.rating,
            "review_count": product.review_count,
            "is_active": product.is_active,
            "tags": [
                product.name.lower(),
                product.brand.lower(),
                product.category.lower()
            ],
            "suggest": {
                "input": [
                    product.name,
                    product.brand,
                    product.category
                ],
                "weight": int((product.rating or 3.0) * 20)
            }
        }
        
        # Index the document
        response = es.index(
            index="products",
            id=product.id,
            document=doc
        )
        
        return {
            "message": "Product indexed successfully",
            "product_id": product.id,
            "result": response["result"]
        }
    
    except Exception as e:
        logger.error(f"Error indexing product: {e}")
        raise HTTPException(status_code=500, detail="Failed to index product")

@app.delete("/products/{product_id}")
async def remove_product_from_index(product_id: int):
    """Remove a product from the search index."""
    try:
        response = es.delete(index="products", id=product_id)
        
        return {
            "message": "Product removed from index",
            "product_id": product_id,
            "result": response["result"]
        }
    
    except Exception as e:
        if "not_found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Product not found in index")
        logger.error(f"Error removing product from index: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove product from index")

@app.get("/analytics/search-performance")
async def get_search_performance():
    """Get search performance analytics."""
    try:
        # Get search performance metrics for the last 24 hours
        agg_body = {
            "query": {
                "range": {
                    "timestamp": {"gte": "now-24h"}
                }
            },
            "size": 0,
            "aggs": {
                "total_searches": {
                    "value_count": {"field": "query.keyword"}
                },
                "avg_search_time": {
                    "avg": {"field": "search_time_ms"}
                },
                "zero_results_rate": {
                    "filter": {"term": {"results_count": 0}},
                    "aggs": {
                        "rate": {
                            "bucket_script": {
                                "buckets_path": {
                                    "zero_results": "_count",
                                    "total": "_parent>total_searches.value"
                                },
                                "script": "params.zero_results / params.total"
                            }
                        }
                    }
                },
                "click_through_rate": {
                    "filter": {"term": {"converted": True}},
                    "aggs": {
                        "rate": {
                            "bucket_script": {
                                "buckets_path": {
                                    "clicks": "_count",
                                    "total": "_parent>total_searches.value"
                                },
                                "script": "params.clicks / params.total"
                            }
                        }
                    }
                },
                "popular_filters": {
                    "nested": {"path": "filters_applied"},
                    "aggs": {
                        "filter_names": {
                            "terms": {"field": "filters_applied.name", "size": 10}
                        }
                    }
                }
            }
        }
        
        response = es.search(index="search_analytics", body=agg_body)
        aggs = response["aggregations"]
        
        return {
            "period": "last_24_hours",
            "total_searches": aggs["total_searches"]["value"],
            "avg_search_time_ms": round(aggs["avg_search_time"]["value"] or 0, 2),
            "zero_results_rate": round(aggs["zero_results_rate"]["rate"]["value"] or 0, 4),
            "click_through_rate": round(aggs["click_through_rate"]["rate"]["value"] or 0, 4),
            "popular_filters": [
                {"filter": bucket["key"], "usage_count": bucket["doc_count"]}
                for bucket in aggs["popular_filters"]["filter_names"]["buckets"]
            ],
            "timestamp": datetime.now()
        }
    
    except Exception as e:
        logger.error(f"Error getting search performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search performance")

# New endpoints for migrated indices

@app.get("/user-sessions")
async def get_user_sessions(
    user_id: Optional[int] = None,
    active_only: bool = False,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """Get user sessions from Elasticsearch."""
    try:
        # Build query
        query_body = {"match_all": {}}
        filters = []
        
        if user_id:
            filters.append({"term": {"user_id": user_id}})
        
        if active_only:
            filters.append({"term": {"is_active": True}})
        
        if filters:
            query_body = {
                "bool": {
                    "must": filters
                }
            }
        
        # Execute search
        search_body = {
            "query": query_body,
            "sort": [{"start_time": {"order": "desc"}}],
            "from": (page - 1) * size,
            "size": size
        }
        
        response = es.search(index="user_sessions", body=search_body)
        
        sessions = []
        for hit in response["hits"]["hits"]:
            session = hit["_source"]
            session["_id"] = hit["_id"]
            sessions.append(session)
        
        return {
            "sessions": sessions,
            "total": response["hits"]["total"]["value"],
            "page": page,
            "size": size
        }
    
    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user sessions")

@app.get("/user-behavior")
async def get_user_behavior(
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200)
):
    """Get user behavior events from Elasticsearch."""
    try:
        # Build query
        filters = []
        
        if user_id:
            filters.append({"term": {"user_id": user_id}})
        
        if event_type:
            filters.append({"term": {"event_type": event_type}})
        
        query_body = {"match_all": {}}
        if filters:
            query_body = {
                "bool": {
                    "must": filters
                }
            }
        
        # Execute search
        search_body = {
            "query": query_body,
            "sort": [{"timestamp": {"order": "desc"}}],
            "from": (page - 1) * size,
            "size": size
        }
        
        response = es.search(index="user_behavior", body=search_body)
        
        behaviors = []
        for hit in response["hits"]["hits"]:
            behavior = hit["_source"]
            behavior["_id"] = hit["_id"]
            behaviors.append(behavior)
        
        return {
            "behaviors": behaviors,
            "total": response["hits"]["total"]["value"],
            "page": page,
            "size": size
        }
    
    except Exception as e:
        logger.error(f"Error getting user behavior: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user behavior")

@app.get("/analytics")
async def get_analytics_data(
    metric_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """Get analytics data from Elasticsearch."""
    try:
        # Build query
        filters = []
        
        if metric_type:
            filters.append({"term": {"metric_type": metric_type}})
        
        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            filters.append({"range": {"date": date_range}})
        
        query_body = {"match_all": {}}
        if filters:
            query_body = {
                "bool": {
                    "must": filters
                }
            }
        
        # Execute search
        search_body = {
            "query": query_body,
            "sort": [{"date": {"order": "desc"}}],
            "from": (page - 1) * size,
            "size": size
        }
        
        response = es.search(index="analytics", body=search_body)
        
        analytics = []
        for hit in response["hits"]["hits"]:
            analytic = hit["_source"]
            analytic["_id"] = hit["_id"]
            analytics.append(analytic)
        
        return {
            "analytics": analytics,
            "total": response["hits"]["total"]["value"],
            "page": page,
            "size": size
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics data")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )