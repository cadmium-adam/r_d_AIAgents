"""
MongoDB FastAPI service for e-commerce flexible schema data.
Handles product reviews, shopping carts, and AI recommendations.
Note: User sessions, behavior tracking, and analytics have been migrated to Elasticsearch.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import logging
from bson import ObjectId
import httpx
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce MongoDB API",
    description="Flexible schema data API using MongoDB for product reviews, shopping carts, and AI recommendations",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb://admin:admin123@localhost:27017/", authSource="admin")
db = client["ecommerce"]


# Pydantic models
class Helpfulness(BaseModel):
    helpful_votes: int
    total_votes: int
    helpfulness_ratio: float


class Moderation(BaseModel):
    status: str
    flagged_reasons: List[str]
    moderator_notes: str


class EngagementReply(BaseModel):
    author: str
    message: str
    timestamp: datetime


class Engagement(BaseModel):
    replies: List[EngagementReply]
    shares: int


class ReviewResponse(BaseModel):
    id: str
    product_id: int
    product_name: str
    product_category: str
    user_id: int
    user_name: str
    rating: int
    title: str
    comment: str
    pros: List[str]
    cons: List[str]
    helpful_votes: int
    total_votes: int
    unhelpful_votes: int
    helpfulness_ratio: float
    verified_purchase: bool
    early_reviewer: bool
    vine_customer: bool
    device_used: str
    review_language: str
    contains_media: bool
    photos: List[str]
    sentiment_score: float
    moderation: Moderation
    engagement: Engagement
    created_at: datetime
    updated_at: datetime


class ReviewCreate(BaseModel):
    product_id: int
    user_id: int
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    title: str
    comment: str


class CartItem(BaseModel):
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float


class CartResponse(BaseModel):
    user_id: int
    items: List[CartItem]
    total_items: int
    subtotal: float
    estimated_total: float


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class PageView(BaseModel):
    page_type: str
    url: str
    timestamp: datetime
    time_spent_seconds: int


class DeviceInfo(BaseModel):
    user_agent: str
    device_type: str
    browser: str
    os: str


class Location(BaseModel):
    ip_address: str
    country: str
    city: str


class UserSessionResponse(BaseModel):
    session_id: str
    user_id: int
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    pages_viewed: List[PageView]
    device_info: DeviceInfo
    location: Location
    referrer: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BehaviorEvent(BaseModel):
    event_type: str
    product_id: Optional[int] = None
    search_query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class RecommendationProduct(BaseModel):
    product_id: int
    product_name: str
    score: float
    reason: str


class RecommendationContext(BaseModel):
    page_type: str
    user_segment: str
    session_activity: str


class RecommendationPerformance(BaseModel):
    impressions: int
    clicks: int
    conversions: int
    ctr: float


class RecommendationResponse(BaseModel):
    user_id: int
    algorithm: str
    products: List[RecommendationProduct]
    context: RecommendationContext
    performance: RecommendationPerformance
    created_at: datetime
    expires_at: datetime


# Helper functions
def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON serializable format."""
    if isinstance(doc, dict):
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                doc[key] = serialize_mongo_doc(value)
            elif isinstance(value, list):
                doc[key] = [
                    serialize_mongo_doc(item) if isinstance(item, dict) else item
                    for item in value
                ]
    return doc


async def fetch_product_from_mssql(product_id: int) -> Optional[Dict[str, Any]]:
    """Fetch product details from MSSQL API service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://localhost:8001/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    f"Product {product_id} not found in MSSQL service: {response.status_code}"
                )
                return None
    except httpx.RequestError as e:
        logger.error(f"Error fetching product {product_id} from MSSQL service: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching product {product_id}: {e}")
        return None


# API Routes


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.get("/reviews/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful_votes)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
):
    """Get reviews for a specific product."""
    try:
        sort_direction = 1 if order == "asc" else -1

        cursor = (
            db.product_reviews.find({"product_id": product_id})
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )

        reviews = []
        for doc in cursor:
            # Parse engagement replies
            engagement_replies = []
            for reply in doc.get("engagement", {}).get("replies", []):
                engagement_replies.append(
                    EngagementReply(
                        author=reply["author"],
                        message=reply["message"],
                        timestamp=reply["timestamp"],
                    )
                )

            reviews.append(
                ReviewResponse(
                    id=str(doc["_id"]),
                    product_id=doc["product_id"],
                    product_name=doc["product_name"],
                    product_category=doc.get("product_category", ""),
                    user_id=doc["user_id"],
                    user_name=doc["user_name"],
                    rating=doc["rating"],
                    title=doc["title"],
                    comment=doc["comment"],
                    pros=doc.get("pros", []),
                    cons=doc.get("cons", []),
                    helpful_votes=doc["helpful_votes"],
                    total_votes=doc.get("total_votes", doc["helpful_votes"]),
                    unhelpful_votes=doc.get("unhelpful_votes", 0),
                    helpfulness_ratio=doc.get("helpfulness_ratio", 1.0),
                    verified_purchase=doc["verified_purchase"],
                    early_reviewer=doc.get("early_reviewer", False),
                    vine_customer=doc.get("vine_customer", False),
                    device_used=doc.get("device_used", "Unknown"),
                    review_language=doc.get("review_language", "en"),
                    contains_media=doc.get("contains_media", False),
                    photos=doc.get("photos", []),
                    sentiment_score=doc.get("sentiment_score", 0.5),
                    moderation=Moderation(
                        status=doc.get("moderation", {}).get("status", "approved"),
                        flagged_reasons=doc.get("moderation", {}).get(
                            "flagged_reasons", []
                        ),
                        moderator_notes=doc.get("moderation", {}).get(
                            "moderator_notes", ""
                        ),
                    ),
                    engagement=Engagement(
                        replies=engagement_replies,
                        shares=doc.get("engagement", {}).get("shares", 0),
                    ),
                    created_at=doc["created_at"],
                    updated_at=doc.get("updated_at", doc["created_at"]),
                )
            )

        return reviews

    except Exception as e:
        logger.error(f"Error fetching reviews for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")


@app.post("/reviews", response_model=ReviewResponse)
async def create_review(review: ReviewCreate):
    """Create a new product review."""
    try:
        # Check if user already reviewed this product
        existing_review = db.product_reviews.find_one(
            {"product_id": review.product_id, "user_id": review.user_id}
        )

        if existing_review:
            raise HTTPException(
                status_code=400, detail="User has already reviewed this product"
            )

        # Create review document with full structure
        review_doc = {
            "product_id": review.product_id,
            "product_name": f"Product {review.product_id}",  # In real app, fetch from product service
            "product_category": "General",  # In real app, fetch from product service
            "user_id": review.user_id,
            "user_name": f"User {review.user_id}",  # In real app, fetch from user service
            "order_id": review.order_id,
            "rating": review.rating,
            "title": review.title,
            "comment": review.comment,
            "pros": [],
            "cons": [],
            "helpful_votes": 0,
            "total_votes": 0,
            "unhelpful_votes": 0,
            "helpfulness_ratio": 1.0,
            "verified_purchase": True,
            "early_reviewer": False,
            "vine_customer": False,
            "device_used": "web",
            "review_language": "en",
            "contains_media": False,
            "photos": [],
            "sentiment_score": 0.5,  # Would be calculated by ML service
            "moderation": {
                "status": "approved",
                "flagged_reasons": [],
                "moderator_notes": "",
            },
            "engagement": {"replies": [], "shares": 0},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = db.product_reviews.insert_one(review_doc)
        review_doc["_id"] = result.inserted_id

        return ReviewResponse(
            id=str(result.inserted_id),
            product_id=review_doc["product_id"],
            product_name=review_doc["product_name"],
            product_category="",
            user_id=review_doc["user_id"],
            user_name=review_doc["user_name"],
            rating=review_doc["rating"],
            title=review_doc["title"],
            comment=review_doc["comment"],
            pros=[],
            cons=[],
            helpful_votes=review_doc["helpful_votes"],
            total_votes=review_doc["helpful_votes"],
            unhelpful_votes=review_doc["unhelpful_votes"],
            helpfulness_ratio=1.0,
            verified_purchase=review_doc["verified_purchase"],
            early_reviewer=False,
            vine_customer=False,
            device_used="Unknown",
            review_language="en",
            contains_media=False,
            photos=review_doc["photos"],
            sentiment_score=review_doc["sentiment_score"],
            moderation=Moderation(
                status=review_doc["moderation"]["status"],
                flagged_reasons=review_doc["moderation"]["flagged_reasons"],
                moderator_notes=review_doc["moderation"]["moderator_notes"],
            ),
            engagement=Engagement(
                replies=[], shares=review_doc["engagement"]["shares"]
            ),
            created_at=review_doc["created_at"],
            updated_at=review_doc["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(status_code=500, detail="Failed to create review")


@app.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(review_id: str):
    """Mark a review as helpful."""
    try:
        result = db.product_reviews.update_one(
            {"_id": ObjectId(review_id)}, {"$inc": {"helpful_votes": 1}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")

        return {"message": "Review marked as helpful"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking review helpful: {e}")
        raise HTTPException(status_code=500, detail="Failed to update review")


@app.get("/cart/{user_id}", response_model=CartResponse)
async def get_shopping_cart(user_id: int):
    """Get user's shopping cart."""
    try:
        cart = db.shopping_carts.find_one({"user_id": user_id})

        if not cart:
            return CartResponse(
                user_id=user_id,
                items=[],
                total_items=0,
                subtotal=0.0,
                estimated_total=0.0,
            )

        cart_items = []
        for item in cart["items"]:
            cart_items.append(
                CartItem(
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    product_image=item.get("product_image"),
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    total_price=item["total_price"],
                )
            )

        return CartResponse(
            user_id=cart["user_id"],
            items=cart_items,
            total_items=cart["total_items"],
            subtotal=cart["subtotal"],
            estimated_total=cart["estimated_total"],
        )

    except Exception as e:
        logger.error(f"Error fetching cart for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch shopping cart")


@app.post("/cart/{user_id}/add")
async def add_to_cart(user_id: int, item: CartItemAdd):
    """Add item to shopping cart."""
    try:
        # Fetch real product details from MSSQL service
        product_data = await fetch_product_from_mssql(item.product_id)

        print(f"Product data fetched: {product_data}")

        if not product_data:
            # Fallback to mock data if MSSQL service unavailable
            logger.warning(f"Using fallback data for product {item.product_id}")
            product_price = 99.99
            product_name = f"Product {item.product_id}"
            product_image = None  # No image available when MSSQL service unavailable
        else:
            product_price = float(product_data["price"])
            product_name = product_data["name"]
            product_image = product_data.get("thumbnail_url")

        # Check if cart exists
        cart = db.shopping_carts.find_one({"user_id": user_id})

        if not cart:
            # Create new cart
            cart_doc = {
                "user_id": user_id,
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": product_name,
                        "product_image": product_image,
                        "quantity": item.quantity,
                        "unit_price": product_price,
                        "total_price": product_price * item.quantity,
                        "added_at": datetime.now(),
                        "saved_for_later": False,
                    }
                ],
                "total_items": item.quantity,
                "subtotal": product_price * item.quantity,
                "estimated_tax": (product_price * item.quantity) * 0.08,
                "estimated_shipping": (
                    9.99 if (product_price * item.quantity) <= 50 else 0.0
                ),
                "estimated_total": (product_price * item.quantity) * 1.08
                + (9.99 if (product_price * item.quantity) <= 50 else 0.0),
                "coupon_code": None,
                "discount_amount": 0.0,
                "session_id": f"sess_{user_id}_current",
                "device_type": "web",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            db.shopping_carts.insert_one(cart_doc)
        else:
            # Update existing cart
            existing_item = next(
                (i for i in cart["items"] if i["product_id"] == item.product_id), None
            )

            if existing_item:
                # Update quantity
                db.shopping_carts.update_one(
                    {"user_id": user_id, "items.product_id": item.product_id},
                    {
                        "$inc": {
                            "items.$.quantity": item.quantity,
                            "items.$.total_price": product_price * item.quantity,
                        },
                        "$set": {"updated_at": datetime.now()},
                    },
                )
            else:
                # Add new item
                new_item = {
                    "product_id": item.product_id,
                    "product_name": product_name,
                    "product_image": product_image,
                    "quantity": item.quantity,
                    "unit_price": product_price,
                    "total_price": product_price * item.quantity,
                    "added_at": datetime.now(),
                    "saved_for_later": False,
                }

                db.shopping_carts.update_one(
                    {"user_id": user_id},
                    {
                        "$push": {"items": new_item},
                        "$set": {"updated_at": datetime.now()},
                    },
                )

            # Recalculate totals
            updated_cart = db.shopping_carts.find_one({"user_id": user_id})
            total_items = sum(item["quantity"] for item in updated_cart["items"])
            subtotal = sum(item["total_price"] for item in updated_cart["items"])
            estimated_tax = subtotal * 0.08
            estimated_shipping = 9.99 if subtotal <= 50 else 0.0
            estimated_total = subtotal + estimated_tax + estimated_shipping

            db.shopping_carts.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "total_items": total_items,
                        "subtotal": subtotal,
                        "estimated_tax": estimated_tax,
                        "estimated_shipping": estimated_shipping,
                        "estimated_total": estimated_total,
                    }
                },
            )

        return {"message": "Item added to cart successfully"}

    except Exception as e:
        logger.error(f"Error adding item to cart: {e}")
        raise HTTPException(status_code=500, detail="Failed to add item to cart")


@app.delete("/cart/{user_id}/item/{product_id}")
async def remove_from_cart(user_id: int, product_id: int):
    """Remove item from shopping cart."""
    try:
        result = db.shopping_carts.update_one(
            {"user_id": user_id}, {"$pull": {"items": {"product_id": product_id}}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        # Recalculate totals
        cart = db.shopping_carts.find_one({"user_id": user_id})
        if cart and cart["items"]:
            total_items = sum(item["quantity"] for item in cart["items"])
            subtotal = sum(item["total_price"] for item in cart["items"])
            estimated_tax = subtotal * 0.08
            estimated_shipping = 9.99 if subtotal <= 50 else 0.0
            estimated_total = subtotal + estimated_tax + estimated_shipping

            db.shopping_carts.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "total_items": total_items,
                        "subtotal": subtotal,
                        "estimated_tax": estimated_tax,
                        "estimated_shipping": estimated_shipping,
                        "estimated_total": estimated_total,
                        "updated_at": datetime.now(),
                    }
                },
            )
        else:
            # Remove empty cart
            db.shopping_carts.delete_one({"user_id": user_id})

        return {"message": "Item removed from cart"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from cart: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove item from cart")


# User sessions have been migrated to Elasticsearch
# @app.get("/users/{user_id}/session", response_model=UserSessionResponse)
# async def get_user_session(user_id: int):
#     """Get user's current or most recent session."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


# User behavior tracking has been migrated to Elasticsearch
# @app.post("/users/{user_id}/behavior")
# async def track_user_behavior(
#     user_id: int, event: BehaviorEvent, background_tasks: BackgroundTasks
# ):
#     """Track user behavior event."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


# Trending products has been migrated to Elasticsearch (uses user_behavior data)
# @app.get("/recommendations/trending")
# async def get_trending_products(limit: int = Query(10, ge=1, le=50)):
#     """Get trending products based on user behavior."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


@app.get("/recommendations/{user_id}", response_model=List[RecommendationResponse])
async def get_user_recommendations(user_id: int, algorithm: Optional[str] = None):
    """Get personalized recommendations for a user."""
    try:
        query = {"user_id": user_id}
        if algorithm:
            query["algorithm"] = algorithm

        recommendations = list(
            db.recommendations.find(query).sort("created_at", -1).limit(5)
        )

        result = []
        for rec in recommendations:
            # Parse recommendation products
            recommendation_products = []
            for product in rec.get("products", []):
                recommendation_products.append(
                    RecommendationProduct(
                        product_id=product["product_id"],
                        product_name=product["product_name"],
                        score=product["score"],
                        reason=product["reason"],
                    )
                )

            result.append(
                RecommendationResponse(
                    user_id=rec["user_id"],
                    algorithm=rec["algorithm"],
                    products=recommendation_products,
                    context=RecommendationContext(
                        page_type=rec.get("context", {}).get("page_type", "unknown"),
                        user_segment=rec.get("context", {}).get(
                            "user_segment", "unknown"
                        ),
                        session_activity=rec.get("context", {}).get(
                            "session_activity", "unknown"
                        ),
                    ),
                    performance=RecommendationPerformance(
                        impressions=rec.get("performance", {}).get("impressions", 0),
                        clicks=rec.get("performance", {}).get("clicks", 0),
                        conversions=rec.get("performance", {}).get("conversions", 0),
                        ctr=rec.get("performance", {}).get("ctr", 0.0),
                    ),
                    created_at=rec["created_at"],
                    expires_at=rec.get("expires_at", rec["created_at"]),
                )
            )

        return result

    except Exception as e:
        logger.error(f"Error fetching recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations")


# Real-time analytics has been migrated to Elasticsearch (uses user_sessions and user_behavior data)
# @app.get("/analytics/realtime")
# async def get_realtime_analytics():
#     """Get real-time analytics data."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


# User sessions have been migrated to Elasticsearch
# @app.get("/user-sessions")
# async def get_user_sessions(limit: int = Query(100, ge=1, le=500)):
#     """Get user sessions data from MongoDB."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


# User behavior tracking has been migrated to Elasticsearch
# @app.get("/user-behavior")
# async def get_user_behavior(
#     limit: int = Query(100, ge=1, le=500),
#     event_type: Optional[str] = None,
#     user_id: Optional[int] = None
# ):
#     """Get user behavior data from MongoDB."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


# Analytics data has been migrated to Elasticsearch
# @app.get("/analytics")
# async def get_analytics_data(limit: int = Query(50, ge=1, le=200)):
#     """Get analytics data from MongoDB."""
#     # This endpoint has been migrated to Elasticsearch API (port 8003)


@app.get("/recommendations")
async def get_recommendations_data(
    limit: int = Query(100, ge=1, le=500),
    algorithm: Optional[str] = None,
    user_id: Optional[int] = None
):
    """Get recommendations data from MongoDB."""
    try:
        # Build query
        query = {}
        if algorithm:
            query["algorithm"] = algorithm
        if user_id:
            query["user_id"] = user_id
            
        recommendations = list(
            db.recommendations.find(query).sort([("created_at", -1)]).limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for rec in recommendations:
            rec["_id"] = str(rec["_id"])
            
        return {"recommendations": recommendations, "count": len(recommendations)}
    except Exception as e:
        logger.error(f"Error fetching recommendations data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations data")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True, log_level="info")
