"""
MongoDB database population script for e-commerce data.
Handles flexible schema data: user sessions, reviews, behavioral data, and real-time analytics.

Usage:
    python populate_data.py [--recreate|--append]

Modes:
    --recreate (default): Drop and recreate collections, overwriting all data
    --append: Add new data to existing collections, preserving existing documents
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from pymongo import MongoClient
from faker import Faker

# Add shared_data to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

fake = Faker()

class MongoDBPopulator:
    """Populates MongoDB with e-commerce data optimized for flexible schemas."""
    
    def __init__(self, append_mode: bool = False):
        self.client = MongoClient(
            'mongodb://admin:admin123@localhost:27017/',
            authSource='admin'
        )
        self.db = self.client['ecommerce']
        self.append_mode = append_mode
        
    def create_collections(self):
        """Create MongoDB collections with appropriate indexes."""
        if self.append_mode:
            print("Append mode: Ensuring collections and indexes exist...")
        else:
            print("Recreate mode: Creating fresh collections and indexes...")
            # Drop existing collections to ensure clean state
            # Note: user_sessions, user_behavior, and analytics have been migrated to Elasticsearch
            collection_names = ['product_reviews', 'shopping_carts', 'recommendations']
            for collection_name in collection_names:
                self.db[collection_name].drop()
            print("Dropped existing collections for clean state.")
        
        # Product reviews collection
        reviews = self.db['product_reviews']
        reviews.create_index([('product_id', 1), ('created_at', -1)])
        reviews.create_index([('user_id', 1)])
        reviews.create_index([('rating', 1)])
        reviews.create_index([('verified_purchase', 1)])
        
        # Shopping carts collection
        carts = self.db['shopping_carts']
        carts.create_index([('user_id', 1)], unique=True)
        carts.create_index([('updated_at', -1)])
        
        # Product recommendations
        recommendations = self.db['recommendations']
        recommendations.create_index([('user_id', 1)])
        recommendations.create_index([('algorithm', 1)])
        recommendations.create_index([('created_at', -1)])
        
        print("Collections and indexes created successfully.")
    
    def insert_user_sessions(self, users: List[Dict[str, Any]]):
        """Generate and insert user session data."""
        print("Generating user sessions...")
        
        sessions = []
        inserted_count = 0
        skipped_count = 0
        
        for user in users:
            if self.append_mode:
                # Check if user already has sessions
                existing_sessions = self.db['user_sessions'].count_documents({'user_id': user['id']})
                if existing_sessions > 0:
                    skipped_count += 1
                    continue
            # Generate 1-5 sessions per user over the last 30 days
            num_sessions = random.randint(1, 5)
            
            for i in range(num_sessions):
                session_start = fake.date_time_between(start_date='-30d', end_date='now')
                duration_minutes = random.choices(
                    [5, 15, 30, 60, 120, 180],
                    weights=[20, 30, 25, 15, 7, 3]
                )[0]
                session_end = session_start + timedelta(minutes=duration_minutes)
                
                # Generate page views during session
                pages_viewed = []
                current_time = session_start
                
                while current_time < session_end:
                    page_types = ['home', 'category', 'product', 'search', 'cart', 'checkout', 'account']
                    page_weights = [15, 20, 30, 15, 10, 5, 5]
                    page_type = random.choices(page_types, weights=page_weights)[0]
                    
                    page_view = {
                        'page_type': page_type,
                        'url': f'/{page_type}' + (f'/{random.randint(1, 1000)}' if page_type in ['product', 'category'] else ''),
                        'timestamp': current_time,
                        'time_spent_seconds': random.randint(10, 300)
                    }
                    pages_viewed.append(page_view)
                    
                    current_time += timedelta(seconds=page_view['time_spent_seconds'] + random.randint(1, 10))
                
                session = {
                    'session_id': f'sess_{user["id"]}_{i}_{int(session_start.timestamp())}',
                    'user_id': user['id'],
                    'start_time': session_start,
                    'end_time': session_end,
                    'duration_minutes': duration_minutes,
                    'pages_viewed': pages_viewed,
                    'device_info': {
                        'user_agent': fake.user_agent(),
                        'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                        'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                        'os': random.choice(['Windows', 'macOS', 'iOS', 'Android', 'Linux'])
                    },
                    'location': {
                        'ip_address': fake.ipv4(),
                        'country': user['shipping_address']['country'],
                        'city': user['shipping_address']['city']
                    },
                    'referrer': random.choice([
                        'google.com', 'facebook.com', 'instagram.com', 'direct', 'email_campaign'
                    ]),
                    'is_active': session_end > (datetime.now() - timedelta(hours=1)),
                    'created_at': session_start,
                    'updated_at': session_end
                }
                
                sessions.append(session)
                inserted_count += 1
        
        if sessions:
            self.db['user_sessions'].insert_many(sessions)
        
        if self.append_mode:
            print(f"User sessions processed: {inserted_count} inserted, {skipped_count} skipped (users already have sessions)")
        else:
            print(f"User sessions inserted successfully: {inserted_count}")
    
    def insert_product_reviews(self, reviews: List[Dict[str, Any]], users: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Insert product reviews with rich metadata."""
        print("Inserting product reviews...")
        
        mongo_reviews = []
        inserted_count = 0
        skipped_count = 0
        
        for review in reviews:
            if self.append_mode:
                # Check if review already exists
                existing_review = self.db['product_reviews'].count_documents({'_id': review['id']})
                if existing_review > 0:
                    skipped_count += 1
                    continue
            # Find the user and product for additional context
            user = next((u for u in users if u['id'] == review['user_id']), None)
            product = next((p for p in products if p['id'] == review['product_id']), None)
            
            if not user or not product:
                continue
            
            # Generate additional review metadata
            mongo_review = {
                '_id': review['id'],
                'product_id': review['product_id'],
                'product_name': review['product_name'],
                'product_category': product['category'],
                'user_id': review['user_id'],
                'user_name': review['user_name'],
                'rating': review['rating'],
                'title': review['title'],
                'comment': review['comment'],
                'pros': review.get('pros', []),
                'cons': review.get('cons', []),
                'helpful_votes': review['helpfulness']['helpful_votes'],
                'total_votes': review['helpfulness']['total_votes'],
                'helpfulness_ratio': review['helpfulness']['helpfulness_ratio'],
                'verified_purchase': review['metadata']['verified_purchase'],
                'early_reviewer': review['metadata'].get('early_reviewer', False),
                'vine_customer': review['metadata'].get('vine_customer', False),
                'device_used': review['metadata'].get('device_used', 'Unknown'),
                'review_language': review['metadata'].get('review_language', 'en'),
                'contains_media': review['metadata'].get('contains_media', False),
                'photos': [
                    f"https://images.example.com/review_{review['id']}_{i}.jpg"
                    for i in range(random.randint(0, 3))
                ] if random.random() < 0.2 else [],  # 20% of reviews have photos
                'sentiment_score': round(random.uniform(0.1, 1.0), 2) if review['rating'] >= 4 
                                 else round(random.uniform(-1.0, 0.2), 2),
                'moderation': {
                    'status': random.choices(['approved', 'pending', 'flagged'], weights=[92, 6, 2])[0],
                    'flagged_reasons': [] if random.random() > 0.05 else random.sample(
                        ['spam', 'inappropriate_language', 'fake_review'], 
                        k=random.randint(1, 2)
                    ),
                    'moderator_notes': ''
                },
                'engagement': {
                    'replies': [
                        {
                            'author': 'Customer Service',
                            'message': "Thank you for your review! We're glad you're satisfied with your purchase.",
                            'timestamp': review['review_date']
                        }
                    ] if random.random() < 0.1 else [],  # 10% get CS replies
                    'shares': random.randint(0, 5)
                },
                'created_at': review['review_date'],
                'updated_at': review['review_date']
            }
            
            mongo_reviews.append(mongo_review)
            inserted_count += 1
        
        if mongo_reviews:
            self.db['product_reviews'].insert_many(mongo_reviews)
        
        if self.append_mode:
            print(f"Product reviews processed: {inserted_count} inserted, {skipped_count} skipped (already exist)")
        else:
            print(f"Product reviews inserted successfully: {inserted_count}")
    
    def insert_shopping_carts(self, users: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Generate shopping cart data for active users."""
        print("Generating shopping carts...")
        
        carts = []
        inserted_count = 0
        skipped_count = 0
        
        # About 30% of users have items in their cart
        active_users = random.sample(users, k=int(len(users) * 0.3))
        
        for user in active_users:
            if self.append_mode:
                # Check if user already has a shopping cart
                existing_cart = self.db['shopping_carts'].count_documents({'user_id': user['id']})
                if existing_cart > 0:
                    skipped_count += 1
                    continue
            num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 8, 2])[0]
            cart_products = random.sample(products, min(num_items, len(products)))
            
            cart_items = []
            total_price = 0.0
            
            for product in cart_products:
                quantity = random.randint(1, 3)
                item_price = product['price'] * quantity
                total_price += item_price
                
                # Use product image if available, otherwise use fallback
                product_image = product.get('images', {}).get('thumbnail', f"https://images.example.com/product_{product['id']}.jpg")
                
                cart_items.append({
                    'product_id': product['id'],
                    'product_name': product['name'],
                    'product_image': product_image,
                    'quantity': quantity,
                    'unit_price': product['price'],
                    'total_price': item_price,
                    'added_at': fake.date_time_between(start_date='-7d', end_date='now'),
                    'saved_for_later': random.choice([True, False]) if random.random() < 0.1 else False
                })
            
            cart = {
                'user_id': user['id'],
                'items': cart_items,
                'total_items': sum(item['quantity'] for item in cart_items),
                'subtotal': round(total_price, 2),
                'estimated_tax': round(total_price * 0.08, 2),
                'estimated_shipping': 0.0 if total_price > 50 else 9.99,
                'estimated_total': round(total_price * 1.08 + (0.0 if total_price > 50 else 9.99), 2),
                'coupon_code': random.choice(['SAVE10', 'FREESHIP', None, None, None]),
                'discount_amount': 0.0,
                'session_id': f'sess_{user["id"]}_current',
                'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                'created_at': min(item['added_at'] for item in cart_items),
                'updated_at': max(item['added_at'] for item in cart_items)
            }
            
            carts.append(cart)
            inserted_count += 1
        
        if carts:
            self.db['shopping_carts'].insert_many(carts)
        
        if self.append_mode:
            print(f"Shopping carts processed: {inserted_count} inserted, {skipped_count} skipped (users already have carts)")
        else:
            print(f"Shopping carts inserted successfully: {inserted_count}")
    
    def insert_user_behavior(self, users: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Generate user behavior tracking data."""
        print("Generating user behavior data...")
        
        behaviors = []
        inserted_count = 0
        skipped_count = 0
        
        for user in users:
            if self.append_mode:
                # Check if user already has behavior data
                existing_behavior = self.db['user_behavior'].count_documents({'user_id': user['id']})
                if existing_behavior > 0:
                    skipped_count += 1
                    continue
            # Generate 10-50 behavior events per user over the last 30 days
            num_events = random.randint(10, 50)
            
            for _ in range(num_events):
                event_time = fake.date_time_between(start_date='-30d', end_date='now')
                event_type = random.choices(
                    ['page_view', 'product_view', 'add_to_cart', 'remove_from_cart', 
                     'search', 'filter_applied', 'wishlist_add', 'purchase'],
                    weights=[30, 25, 15, 5, 15, 5, 3, 2]
                )[0]
                
                behavior = {
                    'user_id': user['id'],
                    'session_id': f'sess_{user["id"]}_{random.randint(1, 5)}',
                    'event_type': event_type,
                    'timestamp': event_time,
                    'page_url': f'/products/{random.randint(1, len(products))}' if 'product' in event_type else f'/{event_type}',
                    'device_info': {
                        'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                        'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
                    }
                }
                
                # Add event-specific data
                if event_type in ['product_view', 'add_to_cart', 'remove_from_cart', 'wishlist_add']:
                    product = random.choice(products)
                    behavior['product_id'] = product['id']
                    behavior['product_name'] = product['name']
                    behavior['product_category'] = product['category']
                    behavior['product_price'] = product['price']
                elif event_type == 'search':
                    search_terms = [
                        'laptop', 'shoes', 'headphones', 'book', 'coffee maker',
                        'jeans', 'smartphone', 'jacket', 'camera', 'yoga mat'
                    ]
                    behavior['search_query'] = random.choice(search_terms)
                    behavior['results_count'] = random.randint(0, 100)
                elif event_type == 'filter_applied':
                    behavior['filters'] = {
                        'category': random.choice(['Electronics', 'Clothing', 'Books']),
                        'price_range': f"{random.randint(0, 500)}-{random.randint(500, 1000)}",
                        'rating': random.choice(['4+', '3+', '5'])
                    }
                elif event_type == 'purchase':
                    behavior['order_total'] = round(random.uniform(25, 500), 2)
                    behavior['items_count'] = random.randint(1, 5)
                
                behaviors.append(behavior)
            
            # Only count users, not individual behavior events
            inserted_count += 1
        
        if behaviors:
            self.db['user_behavior'].insert_many(behaviors)
        
        if self.append_mode:
            print(f"User behavior processed: {inserted_count} users inserted, {skipped_count} users skipped (already have behavior data)")
            if behaviors:
                print(f"  Total behavior events inserted: {len(behaviors)}")
        else:
            print(f"User behavior inserted successfully: {len(behaviors)} events for {inserted_count} users")
    
    def insert_analytics(self):
        """Generate daily analytics data."""
        print("Generating analytics data...")
        
        if self.append_mode:
            # Check if analytics data already exists
            existing_analytics = self.db['analytics'].count_documents({})
            if existing_analytics > 0:
                print(f"Analytics data skipped: {existing_analytics} records already exist")
                return
        
        analytics = []
        
        # Generate analytics for the last 90 days
        for i in range(90):
            date = datetime.now().date() - timedelta(days=i)
            
            # Daily metrics
            daily_metrics = {
                'date': datetime.combine(date, datetime.min.time()),
                'metric_type': 'daily_summary',
                'visitors': {
                    'unique': random.randint(1000, 5000),
                    'returning': random.randint(300, 1500),
                    'new': random.randint(700, 3500)
                },
                'page_views': random.randint(10000, 50000),
                'sessions': random.randint(2000, 10000),
                'bounce_rate': round(random.uniform(0.3, 0.7), 2),
                'avg_session_duration': random.randint(120, 600),
                'conversion_rate': round(random.uniform(0.01, 0.05), 4),
                'revenue': round(random.uniform(5000, 25000), 2),
                'orders': random.randint(50, 300),
                'avg_order_value': round(random.uniform(50, 200), 2),
                'top_products': [
                    {'product_id': random.randint(1, 1000), 'views': random.randint(100, 1000)}
                    for _ in range(10)
                ],
                'top_categories': [
                    {'category': cat, 'revenue': round(random.uniform(1000, 5000), 2)}
                    for cat in ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
                ],
                'traffic_sources': {
                    'organic': round(random.uniform(0.3, 0.5), 2),
                    'direct': round(random.uniform(0.2, 0.4), 2),
                    'social': round(random.uniform(0.1, 0.2), 2),
                    'email': round(random.uniform(0.05, 0.15), 2),
                    'paid': round(random.uniform(0.05, 0.2), 2)
                },
                'device_breakdown': {
                    'desktop': round(random.uniform(0.4, 0.6), 2),
                    'mobile': round(random.uniform(0.3, 0.5), 2),
                    'tablet': round(random.uniform(0.05, 0.15), 2)
                },
                'created_at': datetime.combine(date, datetime.min.time()),
                'updated_at': datetime.now()
            }
            
            analytics.append(daily_metrics)
        
        self.db['analytics'].insert_many(analytics)
        print(f"Analytics data inserted successfully: {len(analytics)} records")
    
    def insert_recommendations(self, users: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Generate recommendation data for users."""
        print("Generating recommendation data...")
        
        recommendations = []
        inserted_count = 0
        skipped_count = 0
        algorithms = ['collaborative_filtering', 'content_based', 'hybrid', 'trending', 'seasonal']
        
        for user in users:
            if self.append_mode:
                # Check if user already has recommendations
                existing_recommendations = self.db['recommendations'].count_documents({'user_id': user['id']})
                if existing_recommendations > 0:
                    skipped_count += 1
                    continue
            # Generate recommendations using different algorithms
            for algorithm in random.sample(algorithms, k=random.randint(2, 4)):
                # Select 5-15 products to recommend (limited by available products)
                max_recommendations = min(len(products), 15)
                min_recommendations = min(5, len(products))
                recommended_products = random.sample(products, k=random.randint(min_recommendations, max_recommendations))
                
                rec_data = {
                    'user_id': user['id'],
                    'algorithm': algorithm,
                    'products': [
                        {
                            'product_id': p['id'],
                            'product_name': p['name'],
                            'score': round(random.uniform(0.1, 1.0), 3),
                            'reason': random.choice([
                                'Based on your browsing history',
                                'Customers who bought this also bought',
                                'Popular in your area',
                                'Trending now',
                                'Similar to items you liked'
                            ])
                        }
                        for p in recommended_products
                    ],
                    'context': {
                        'page_type': random.choice(['homepage', 'product_page', 'cart', 'category']),
                        'user_segment': random.choice(['new_user', 'returning_customer', 'vip', 'at_risk']),
                        'session_activity': random.choice(['browsing', 'searching', 'comparing'])
                    },
                    'performance': {
                        'impressions': random.randint(0, 100),
                        'clicks': random.randint(0, 10),
                        'conversions': random.randint(0, 3),
                        'ctr': round(random.uniform(0.01, 0.15), 4)
                    },
                    'created_at': fake.date_time_between(start_date='-7d', end_date='now'),
                    'expires_at': fake.date_time_between(start_date='now', end_date='+7d')
                }
                
                recommendations.append(rec_data)
            
            # Only count users, not individual recommendation sets
            inserted_count += 1
        
        if recommendations:
            self.db['recommendations'].insert_many(recommendations)
        
        if self.append_mode:
            print(f"Recommendations processed: {inserted_count} users inserted, {skipped_count} users skipped (already have recommendations)")
            if recommendations:
                print(f"  Total recommendation sets inserted: {len(recommendations)}")
        else:
            print(f"Recommendations inserted successfully: {len(recommendations)} sets for {inserted_count} users")
    
    def populate_database(self):
        """Main method to populate MongoDB with all data."""
        mode_text = "append mode" if self.append_mode else "recreate mode"
        print(f"Starting MongoDB database population ({mode_text})...")
        
        # Load data from shared_data directory
        data_dir = os.path.join("..", "..", "shared_data")
        
        # Check if all required data files exist
        required_files = ["products.json", "users.json", "orders.json", "reviews.json"]
        for filename in required_files:
            filepath = os.path.join(data_dir, filename)
            if not os.path.exists(filepath):
                print(f"❌ Error: {filename} not found at {filepath}")
                print("Please run the data generator first:")
                print("cd shared_data && uv run data_generator.py")
                sys.exit(1)
        
        print("Loading existing data...")
        with open(os.path.join(data_dir, "products.json")) as f:
            data = {"products": json.load(f)}
        with open(os.path.join(data_dir, "users.json")) as f:
            data["users"] = json.load(f)
        with open(os.path.join(data_dir, "orders.json")) as f:
            data["orders"] = json.load(f)
        with open(os.path.join(data_dir, "reviews.json")) as f:
            data["reviews"] = json.load(f)
        
        # Create collections and indexes
        self.create_collections()
        
        # Insert all data
        # Note: user_sessions, user_behavior, and analytics have been migrated to Elasticsearch
        # self.insert_user_sessions(data["users"])  # Migrated to Elasticsearch
        self.insert_product_reviews(data["reviews"], data["users"], data["products"])
        self.insert_shopping_carts(data["users"], data["products"])
        # self.insert_user_behavior(data["users"], data["products"])  # Migrated to Elasticsearch
        # self.insert_analytics()  # Migrated to Elasticsearch
        self.insert_recommendations(data["users"], data["products"])
        
        print("MongoDB database population completed successfully!")
        
        # Print summary
        collections = ['product_reviews', 'shopping_carts', 'recommendations']
        for collection in collections:
            count = self.db[collection].count_documents({})
            print(f"{collection}: {count} documents")
        
        print("\nNote: user_sessions, user_behavior, and analytics collections have been migrated to Elasticsearch")

def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Populate MongoDB database with e-commerce data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python populate_data.py                 # Recreate collections (default)
    python populate_data.py --recreate      # Recreate collections explicitly  
    python populate_data.py --append        # Add to existing collections
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--recreate", 
        action="store_true", 
        default=True,
        help="Drop and recreate collections, overwriting all data (default)"
    )
    mode_group.add_argument(
        "--append", 
        action="store_true",
        help="Add new data to existing collections, preserving existing documents"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    append_mode = args.append
    
    if append_mode:
        print("🔄 Running in APPEND mode - existing data will be preserved")
    else:
        print("🔄 Running in RECREATE mode - collections will be recreated")
        print("⚠️  WARNING: This will destroy all existing data!")
        
    try:
        populator = MongoDBPopulator(append_mode=append_mode)
        populator.populate_database()
        
        if append_mode:
            print("✅ Database append completed successfully!")
        else:
            print("✅ Database recreation completed successfully!")
            
    except Exception as e:
        print(f"❌ Error populating MongoDB database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Close the connection
        if 'populator' in locals():
            populator.client.close()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())