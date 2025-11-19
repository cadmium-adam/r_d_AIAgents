"""
Review generation functionality.
Handles product review creation with realistic patterns and content.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from faker import Faker

from .base_generator import BaseGenerator
from .content_generator import ContentGenerator


class ReviewGenerator(BaseGenerator):
    """Handles review generation with realistic data."""

    def __init__(self, content_generator: ContentGenerator = None, **kwargs):
        super().__init__(**kwargs)
        self.content_generator = content_generator or ContentGenerator()

    def generate_review_helpfulness(self) -> Dict[str, int]:
        """Generate review helpfulness metrics."""
        helpful_votes = random.randint(0, 100)
        total_votes = helpful_votes + random.randint(0, 20)
        
        return {
            "helpful_votes": helpful_votes,
            "total_votes": total_votes,
            "helpfulness_ratio": round(helpful_votes / total_votes, 2) if total_votes > 0 else 0
        }

    def generate_review_metadata(self) -> Dict[str, Any]:
        """Generate additional review metadata."""
        return {
            "verified_purchase": random.choice([True, True, True, False]),  # 75% verified
            "early_reviewer": random.choice([True, False]),
            "vine_customer": random.choice([True, False]) if random.random() < 0.05 else False,  # 5% vine
            "device_used": random.choice(["Mobile", "Desktop", "Tablet"]),
            "review_language": "en",
            "contains_media": random.choice([True, False]) if random.random() < 0.2 else False,  # 20% with media
        }

    def determine_rating_distribution(self, base_rating: float) -> int:
        """Determine review rating based on product's base rating."""
        # Create realistic distribution around the product's average rating
        if base_rating >= 4.5:
            weights = [1, 2, 5, 15, 77]  # Mostly 4-5 stars
        elif base_rating >= 4.0:
            weights = [2, 3, 8, 25, 62]  # Good distribution
        elif base_rating >= 3.5:
            weights = [5, 8, 15, 35, 37]  # Mixed reviews
        elif base_rating >= 3.0:
            weights = [10, 15, 25, 30, 20]  # More varied
        else:
            weights = [25, 20, 25, 20, 10]  # Poor product
        
        return random.choices([1, 2, 3, 4, 5], weights=weights)[0]

    def generate_review_timing(self, order_date: datetime, product_category: str) -> datetime:
        """Generate realistic review timing based on order date and product type."""
        # Different products get reviewed at different intervals
        if product_category in ["Electronics", "Books"]:
            # Quick to review - people are excited or have immediate opinions
            days_after = random.randint(1, 30)
        elif product_category in ["Clothing", "Sports"]:
            # Medium time - need to try the product
            days_after = random.randint(3, 60)
        else:  # Home & Garden
            # Longer time - need to use the product for a while
            days_after = random.randint(7, 90)
        
        return order_date + timedelta(days=days_after)

    def generate_review(
        self,
        review_id: int,
        user: Dict[str, Any],
        product: Dict[str, Any],
        order_date: datetime = None
    ) -> Dict[str, Any]:
        """Generate a single review with all attributes."""
        
        # Determine rating based on product's average rating
        rating = self.determine_rating_distribution(product.get("rating", 4.0))
        
        # Generate review content using content generator
        review_content = self.content_generator.generate_llm_review(
            product["name"], 
            product["category"], 
            rating, 
            product.get("features", {})
        )
        
        # Generate review timing
        if order_date is None:
            review_date = self.fake.date_time_between(start_date="-1y", end_date="now")
        else:
            review_date = self.generate_review_timing(order_date, product["category"])
        
        # Generate helpfulness metrics
        helpfulness = self.generate_review_helpfulness()
        
        # Generate metadata
        metadata = self.generate_review_metadata()
        
        review = {
            "id": review_id,
            "product_id": product["id"],
            "product_name": product["name"],
            "user_id": user["id"],
            "user_name": f"{user['first_name']} {user['last_name'][0]}.",  # Anonymized
            "rating": rating,
            "title": review_content["title"],
            "comment": review_content["comment"],
            "pros": self.generate_pros_cons(product, rating)["pros"],
            "cons": self.generate_pros_cons(product, rating)["cons"],
            "helpfulness": helpfulness,
            "metadata": metadata,
            "review_date": review_date,
            "created_at": review_date,
            "updated_at": review_date,
        }
        
        return review

    def generate_pros_cons(self, product: Dict[str, Any], rating: int) -> Dict[str, List[str]]:
        """Generate product pros and cons based on rating and features."""
        category = product.get("category", "")
        features = product.get("features", {})
        
        all_pros = {
            "Electronics": ["Great performance", "Good build quality", "Easy to use", "Good value", "Fast delivery"],
            "Clothing": ["Comfortable fit", "Good quality fabric", "Nice color", "True to size", "Stylish design"],
            "Books": ["Well written", "Informative", "Easy to read", "Good research", "Engaging content"],
            "Home & Garden": ["Works as expected", "Good quality", "Easy to install", "Durable", "Good design"],
            "Sports": ["Good quality", "Comfortable", "Durable", "Good value", "Works well"]
        }
        
        all_cons = {
            "Electronics": ["Battery life could be better", "Expensive", "Setup was confusing", "Not as described"],
            "Clothing": ["Runs small", "Fabric quality poor", "Color different than expected", "Expensive"],
            "Books": ["Too technical", "Poor editing", "Outdated information", "Boring content"],
            "Home & Garden": ["Installation difficult", "Instructions unclear", "Build quality poor", "Overpriced"],
            "Sports": ["Uncomfortable", "Poor durability", "Not as expected", "Sizing issues"]
        }
        
        pros = []
        cons = []
        
        if rating >= 4:
            # High rating - more pros, fewer cons
            pros = random.sample(all_pros.get(category, all_pros["Electronics"]), random.randint(2, 4))
            if rating == 4:
                cons = random.sample(all_cons.get(category, all_cons["Electronics"]), random.randint(0, 1))
        elif rating == 3:
            # Mixed rating - balanced pros and cons
            pros = random.sample(all_pros.get(category, all_pros["Electronics"]), random.randint(1, 2))
            cons = random.sample(all_cons.get(category, all_cons["Electronics"]), random.randint(1, 2))
        else:
            # Low rating - more cons, fewer pros
            if rating == 2:
                pros = random.sample(all_pros.get(category, all_pros["Electronics"]), random.randint(0, 1))
            cons = random.sample(all_cons.get(category, all_cons["Electronics"]), random.randint(2, 3))
        
        return {"pros": pros, "cons": cons}

    def generate_reviews_for_products(
        self,
        products: List[Dict[str, Any]],
        users: List[Dict[str, Any]],
        orders: List[Dict[str, Any]] = None,
        reviews_per_product_range: tuple = (0, 20),
        starting_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate reviews for products."""
        reviews = []
        review_id = starting_id
        
        # Create a mapping of orders to products for realistic review timing
        order_product_map = {}
        if orders:
            for order in orders:
                for item in order.get("items", []):
                    product_id = item["product_id"]
                    user_id = order["user_id"]
                    order_date = order["order_date"]
                    
                    key = (product_id, user_id)
                    if key not in order_product_map:
                        order_product_map[key] = order_date
        
        for product in products:
            # Determine number of reviews based on product rating and review count
            base_reviews = product.get("review_count", 0)
            if base_reviews > 0:
                num_reviews = min(base_reviews, random.randint(*reviews_per_product_range))
            else:
                num_reviews = random.randint(0, reviews_per_product_range[1] // 2)  # Fewer reviews for unrated products
            
            # Select random users to review this product
            review_users = random.sample(users, min(num_reviews, len(users)))
            
            for user in review_users:
                # Check if this user ordered this product
                order_date = order_product_map.get((product["id"], user["id"]))
                
                review = self.generate_review(review_id, user, product, order_date)
                reviews.append(review)
                review_id += 1
                
                if review_id % 100 == 0:
                    print(f"Generated {review_id - 1} reviews...")
        
        return reviews