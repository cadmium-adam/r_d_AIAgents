"""
Elasticsearch database population script for e-commerce data.
Handles search indices, analytics, and search optimization data.

Usage:
    python populate_data.py [--recreate|--append]

Modes:
    --recreate (default): Drop and recreate indices, overwriting all data
    --append: Add new data to existing indices, preserving existing documents
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from elasticsearch import Elasticsearch, helpers
from faker import Faker

# Add shared_data to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

fake = Faker()


class ElasticsearchPopulator:
    """Populates Elasticsearch with e-commerce search and analytics data."""

    def __init__(self, append_mode: bool = False):
        self.es = Elasticsearch(
            "http://localhost:9200",
            request_timeout=60
        )
        self.append_mode = append_mode

    def wait_for_elasticsearch(self, max_retries=30):
        """Wait for Elasticsearch to be ready."""
        for i in range(max_retries):
            try:
                if self.es.ping():
                    print("Elasticsearch is ready!")
                    return True
                print(f"Waiting for Elasticsearch... (attempt {i+1}/{max_retries})")
                import time

                time.sleep(2)
            except Exception as e:
                print(f"Elasticsearch not ready: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                import time

                time.sleep(2)

        raise Exception("Elasticsearch is not available after waiting")

    def create_indices(self):
        """Create Elasticsearch indices with appropriate mappings."""
        if self.append_mode:
            print("Append mode: Ensuring indices and mappings exist...")
        else:
            print("Recreate mode: Creating fresh indices and mappings...")

        # Products index - for product search
        products_mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "autocomplete": {
                                "type": "text",
                                "analyzer": "autocomplete",
                                "search_analyzer": "standard",
                            },
                        },
                    },
                    "description": {"type": "text", "analyzer": "standard"},
                    "category": {
                        "type": "keyword",
                        "fields": {"text": {"type": "text"}},
                    },
                    "brand": {"type": "keyword", "fields": {"text": {"type": "text"}}},
                    "price": {"type": "float"},
                    "stock_quantity": {"type": "integer"},
                    "rating": {"type": "float"},
                    "review_count": {"type": "integer"},
                    "is_active": {"type": "boolean"},
                    "tags": {"type": "keyword"},
                    "attributes": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "keyword"},
                            "value": {"type": "keyword"},
                        },
                    },
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "suggest": {
                        "type": "completion",
                        "analyzer": "simple",
                        "preserve_separators": True,
                        "preserve_position_increments": True,
                        "max_input_length": 50,
                    },
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "autocomplete": {
                            "tokenizer": "autocomplete",
                            "filter": ["lowercase"],
                        }
                    },
                    "tokenizer": {
                        "autocomplete": {
                            "type": "edge_ngram",
                            "min_gram": 2,
                            "max_gram": 10,
                            "token_chars": ["letter", "digit"],
                        }
                    },
                }
            },
        }

        # Search analytics index
        search_analytics_mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "query": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword"}},
                    },
                    "user_id": {"type": "integer"},
                    "session_id": {"type": "keyword"},
                    "results_count": {"type": "integer"},
                    "clicked_product_id": {"type": "integer"},
                    "clicked_position": {"type": "integer"},
                    "search_time_ms": {"type": "integer"},
                    "filters_applied": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "keyword"},
                            "value": {"type": "keyword"},
                        },
                    },
                    "device_type": {"type": "keyword"},
                    "location": {"type": "geo_point"},
                    "converted": {"type": "boolean"},
                }
            }
        }

        # Popular searches index
        popular_searches_mapping = {
            "mappings": {
                "properties": {
                    "query": {"type": "keyword"},
                    "search_count": {"type": "integer"},
                    "last_searched": {"type": "date"},
                    "trending_score": {"type": "float"},
                    "category": {"type": "keyword"},
                    "suggestions": {"type": "keyword"},
                }
            }
        }

        # User sessions index - migrated from MongoDB
        user_sessions_mapping = {
            "mappings": {
                "properties": {
                    "session_id": {"type": "keyword"},
                    "user_id": {"type": "integer"},
                    "start_time": {"type": "date"},
                    "end_time": {"type": "date"},
                    "duration_minutes": {"type": "float"},
                    "pages_viewed": {
                        "type": "nested",
                        "properties": {
                            "url": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "time_spent_seconds": {"type": "integer"}
                        }
                    },
                    "device_info": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "os": {"type": "keyword"},
                            "browser": {"type": "keyword"},
                            "screen_resolution": {"type": "keyword"}
                        }
                    },
                    "location": {
                        "properties": {
                            "country": {"type": "keyword"},
                            "city": {"type": "keyword"},
                            "ip_address": {"type": "ip"}
                        }
                    },
                    "referrer": {"type": "keyword"},
                    "is_active": {"type": "boolean"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        }

        # User behavior index - migrated from MongoDB
        user_behavior_mapping = {
            "mappings": {
                "properties": {
                    "user_id": {"type": "integer"},
                    "session_id": {"type": "keyword"},
                    "event_type": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "page_url": {"type": "keyword"},
                    "device_info": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "os": {"type": "keyword"},
                            "browser": {"type": "keyword"}
                        }
                    },
                    "product_id": {"type": "integer"},
                    "search_query": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "filters": {
                        "properties": {
                            "category": {"type": "keyword"},
                            "price_range": {"type": "keyword"},
                            "brand": {"type": "keyword"}
                        }
                    },
                    "order_total": {"type": "float"},
                    "items_count": {"type": "integer"}
                }
            }
        }

        # Analytics index - migrated from MongoDB
        analytics_mapping = {
            "mappings": {
                "properties": {
                    "date": {"type": "date"},
                    "metric_type": {"type": "keyword"},
                    "unique_visitors": {"type": "integer"},
                    "returning_visitors": {"type": "integer"},
                    "new_visitors": {"type": "integer"},
                    "page_views": {"type": "integer"},
                    "sessions": {"type": "integer"},
                    "bounce_rate": {"type": "float"},
                    "avg_session_duration": {"type": "float"},
                    "conversion_rate": {"type": "float"},
                    "revenue": {"type": "float"},
                    "orders": {"type": "integer"},
                    "avg_order_value": {"type": "float"},
                    "top_products": {
                        "type": "nested",
                        "properties": {
                            "product_id": {"type": "integer"},
                            "name": {"type": "keyword"},
                            "views": {"type": "integer"},
                            "sales": {"type": "integer"}
                        }
                    },
                    "top_categories": {
                        "type": "nested",
                        "properties": {
                            "category": {"type": "keyword"},
                            "views": {"type": "integer"},
                            "sales": {"type": "integer"}
                        }
                    },
                    "traffic_sources": {
                        "properties": {
                            "direct": {"type": "integer"},
                            "search": {"type": "integer"},
                            "social": {"type": "integer"},
                            "referral": {"type": "integer"}
                        }
                    },
                    "device_breakdown": {
                        "properties": {
                            "desktop": {"type": "integer"},
                            "mobile": {"type": "integer"},
                            "tablet": {"type": "integer"}
                        }
                    }
                }
            }
        }

        # Create indices
        indices = {
            "products": products_mapping,
            "search_analytics": search_analytics_mapping,
            "popular_searches": popular_searches_mapping,
            "user_sessions": user_sessions_mapping,
            "user_behavior": user_behavior_mapping,
            "analytics": analytics_mapping,
        }

        for index_name, mapping in indices.items():
            if self.append_mode:
                # In append mode, only create index if it doesn't exist
                if not self.es.indices.exists(index=index_name):
                    self.es.indices.create(index=index_name, body=mapping)
                    print(f"Created index: {index_name}")
                else:
                    print(f"Index already exists: {index_name}")
            else:
                # In recreate mode, drop and recreate indices
                if self.es.indices.exists(index=index_name):
                    self.es.indices.delete(index=index_name)
                    print(f"Dropped existing index: {index_name}")

                self.es.indices.create(index=index_name, body=mapping)
                print(f"Created index: {index_name}")

        print("Indices setup completed successfully.")

    def generate_product_search_data(
        self, products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform products for Elasticsearch indexing."""
        search_products = []

        for product in products:
            # Generate search-optimized tags
            tags = []
            tags.extend(product["name"].lower().split())
            tags.extend(product["brand"].lower().split())
            tags.append(product["category"].lower())

            # Add feature tags based on category
            if product["category"] == "Electronics":
                tags.extend(["tech", "gadget", "digital"])
            elif product["category"] == "Clothing":
                tags.extend(["fashion", "apparel", "wear"])
            elif product["category"] == "Books":
                tags.extend(["reading", "literature", "education"])
            elif product["category"] == "Home & Garden":
                tags.extend(["home", "house", "garden", "living"])
            elif product["category"] == "Sports":
                tags.extend(["fitness", "exercise", "active", "outdoor"])

            # Generate product attributes for faceted search
            attributes = [
                {"name": "brand", "value": product["brand"]},
                {
                    "name": "price_range",
                    "value": self.get_price_range(product["price"]),
                },
                {"name": "rating", "value": str(int(product["rating"]))},
            ]

            # Add enhanced features if available
            if "features" in product and product["features"]:
                for feature_name, feature_value in product["features"].items():
                    if feature_value:
                        attributes.append(
                            {"name": feature_name, "value": str(feature_value)}
                        )

            # Add category-specific attributes
            if product["category"] == "Clothing":
                attributes.extend(
                    [
                        {
                            "name": "size",
                            "value": random.choice(["XS", "S", "M", "L", "XL", "XXL"]),
                        },
                        {
                            "name": "color",
                            "value": random.choice(
                                ["Black", "White", "Blue", "Red", "Green"]
                            ),
                        },
                    ]
                )

            # Create suggestion input for autocomplete
            suggest_input = [product["name"], product["brand"], product["category"]]
            suggest_input.extend(product["name"].split())

            # Add product images if available
            images = product.get(
                "images",
                {
                    "main_image": f"https://images.example.com/product_{product['id']}.jpg",
                    "thumbnail": f"https://images.example.com/product_{product['id']}_thumb.jpg",
                    "gallery": [
                        f"https://images.example.com/product_{product['id']}_gallery_{i}.jpg"
                        for i in range(1, 3)
                    ],
                },
            )

            search_product = {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "category": product["category"],
                "brand": product["brand"],
                "price": product["price"],
                "stock_quantity": product["stock_quantity"],
                "rating": product["rating"],
                "review_count": product["review_count"],
                "is_active": product.get("in_stock", True),
                "tags": list(set(tags)),  # Remove duplicates
                "attributes": attributes,
                "images": images,
                "created_at": datetime.fromisoformat(product["created_at"].replace(' ', 'T')),
                "updated_at": datetime.fromisoformat(product["updated_at"].replace(' ', 'T')),
                "suggest": {
                    "input": suggest_input,
                    "weight": int(product["rating"] * 20),  # Boost popular items
                },
            }

            search_products.append(search_product)

        return search_products

    def get_price_range(self, price: float) -> str:
        """Categorize price into ranges for faceted search."""
        if price < 25:
            return "Under $25"
        elif price < 50:
            return "$25 - $50"
        elif price < 100:
            return "$50 - $100"
        elif price < 250:
            return "$100 - $250"
        elif price < 500:
            return "$250 - $500"
        else:
            return "Over $500"

    def index_products(self, products: List[Dict[str, Any]]):
        """Index products for search."""
        print(f"Indexing {len(products)} products...")

        search_products = self.generate_product_search_data(products)

        # Filter out existing products in append mode
        actions = []
        inserted_count = 0
        skipped_count = 0
        
        for product in search_products:
            if self.append_mode:
                # Check if product already exists
                try:
                    existing = self.es.get(index="products", id=product["id"], _source=False)
                    if existing:
                        skipped_count += 1
                        continue
                except:
                    # Product doesn't exist, so we can index it
                    pass
            
            action = {"_index": "products", "_id": product["id"], "_source": product}
            actions.append(action)
            inserted_count += 1

        # Use bulk helper for efficient indexing
        if actions:
            try:
                success, failed = helpers.bulk(self.es, actions, chunk_size=100, raise_on_error=False)
                if failed:
                    print(f"Failed to index {len(failed)} documents:")
                    for item in failed:
                        print(f"  Error: {item}")
            except Exception as e:
                print(f"Bulk indexing error: {e}")
                raise

            # Refresh index to make documents searchable immediately
            self.es.indices.refresh(index="products")

        if self.append_mode:
            print(f"Products processed: {inserted_count} indexed, {skipped_count} skipped (already exist)")
        else:
            print(f"Products indexed successfully: {inserted_count}")

    def generate_search_analytics(
        self, users: List[Dict[str, Any]], products: List[Dict[str, Any]]
    ):
        """Generate realistic search analytics data."""
        print("Generating search analytics...")
        
        if self.append_mode:
            # Check if analytics data already exists
            try:
                count = self.es.count(index="search_analytics")["count"]
                if count > 0:
                    print(f"Search analytics data skipped: {count} records already exist")
                    return
            except:
                # Index might not exist yet, continue
                pass

        search_queries = [
            "laptop",
            "smartphone",
            "headphones",
            "shoes",
            "jeans",
            "book",
            "coffee maker",
            "camera",
            "tablet",
            "jacket",
            "sneakers",
            "watch",
            "keyboard",
            "mouse",
            "dress",
            "sweater",
            "bluetooth speaker",
            "yoga mat",
            "backpack",
            "sunglasses",
        ]

        analytics = []

        # Generate search events for the last 30 days
        for i in range(5000):  # 5000 search events
            user = random.choice(users)
            query = random.choice(search_queries)

            # Add some typos and variations
            if random.random() < 0.1:  # 10% have typos
                query = self.introduce_typo(query)

            search_time = fake.date_time_between(start_date="-30d", end_date="now")
            results_count = random.randint(0, 100)

            # Determine if user clicked on a result
            clicked_product_id = None
            clicked_position = None
            converted = False

            if results_count > 0 and random.random() < 0.3:  # 30% click rate
                clicked_position = random.choices(
                    range(1, min(21, results_count + 1)),  # Top 20 results
                    weights=[
                        20,
                        15,
                        12,
                        10,
                        8,
                        6,
                        5,
                        4,
                        3,
                        2,
                        2,
                        2,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                        1,
                    ][: min(20, results_count)],
                )[0]
                clicked_product_id = random.choice(products)["id"]
                converted = random.random() < 0.15  # 15% conversion rate on clicks

            # Generate realistic filters
            filters_applied = []
            if random.random() < 0.4:  # 40% use filters
                if random.random() < 0.6:
                    filters_applied.append(
                        {
                            "name": "category",
                            "value": random.choice(
                                [
                                    "Electronics",
                                    "Clothing",
                                    "Books",
                                    "Home & Garden",
                                    "Sports",
                                ]
                            ),
                        }
                    )
                if random.random() < 0.3:
                    filters_applied.append(
                        {
                            "name": "price_range",
                            "value": random.choice(
                                ["Under $25", "$25 - $50", "$50 - $100", "$100 - $250"]
                            ),
                        }
                    )
                if random.random() < 0.2:
                    filters_applied.append(
                        {"name": "rating", "value": random.choice(["4", "5"])}
                    )

            analytic = {
                "timestamp": search_time,
                "query": query,
                "user_id": user["id"],
                "session_id": f'sess_{user["id"]}_{random.randint(1, 5)}',
                "results_count": results_count,
                "clicked_product_id": clicked_product_id,
                "clicked_position": clicked_position,
                "search_time_ms": random.randint(50, 500),
                "filters_applied": filters_applied,
                "device_type": random.choice(["desktop", "mobile", "tablet"]),
                "location": {
                    "lat": float(fake.latitude()),
                    "lon": float(fake.longitude()),
                },
                "converted": converted,
            }

            analytics.append(analytic)

        # Bulk index analytics
        actions = []
        for analytic in analytics:
            action = {"_index": "search_analytics", "_source": analytic}
            actions.append(action)

        helpers.bulk(self.es, actions, chunk_size=100)
        self.es.indices.refresh(index="search_analytics")

        print(f"Search analytics indexed successfully: {len(analytics)} records")

    def introduce_typo(self, word: str) -> str:
        """Introduce a realistic typo into a word."""
        if len(word) <= 2:
            return word

        typo_types = ["transpose", "substitute", "insert", "delete"]
        typo_type = random.choice(typo_types)

        chars = list(word)

        if typo_type == "transpose" and len(chars) > 1:
            # Swap two adjacent characters
            pos = random.randint(0, len(chars) - 2)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
        elif typo_type == "substitute":
            # Replace one character
            pos = random.randint(0, len(chars) - 1)
            chars[pos] = random.choice("abcdefghijklmnopqrstuvwxyz")
        elif typo_type == "insert":
            # Insert a random character
            pos = random.randint(0, len(chars))
            chars.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
        elif typo_type == "delete" and len(chars) > 1:
            # Delete one character
            pos = random.randint(0, len(chars) - 1)
            del chars[pos]

        return "".join(chars)

    def generate_popular_searches(self):
        """Generate popular searches data."""
        print("Generating popular searches...")
        
        if self.append_mode:
            # Check if popular searches data already exists
            try:
                count = self.es.count(index="popular_searches")["count"]
                if count > 0:
                    print(f"Popular searches data skipped: {count} records already exist")
                    return
            except:
                # Index might not exist yet, continue
                pass

        # Aggregate search analytics to find popular searches
        agg_query = {
            "size": 0,
            "aggs": {
                "popular_queries": {
                    "terms": {"field": "query.keyword", "size": 100},
                    "aggs": {
                        "last_searched": {"max": {"field": "timestamp"}},
                        "avg_results": {"avg": {"field": "results_count"}},
                    },
                }
            },
        }

        result = self.es.search(index="search_analytics", body=agg_query)

        popular_searches = []
        for bucket in result["aggregations"]["popular_queries"]["buckets"]:
            query = bucket["key"]
            search_count = bucket["doc_count"]
            last_searched = bucket["last_searched"]["value_as_string"]
            avg_results = bucket["avg_results"]["value"]

            # Calculate trending score (more recent searches score higher)
            last_searched_dt = datetime.fromisoformat(
                last_searched.replace("Z", "+00:00")
            )
            days_ago = (
                datetime.now().replace(tzinfo=last_searched_dt.tzinfo)
                - last_searched_dt
            ).days
            trending_score = search_count * (1 / (days_ago + 1))

            # Categorize the search query
            category = "general"
            for cat in ["electronics", "clothing", "books", "home", "sports"]:
                if cat in query.lower():
                    category = cat
                    break

            # Generate related suggestions
            suggestions = [
                f"{query} sale",
                f"{query} review",
                f"best {query}",
                f"{query} price",
                f"cheap {query}",
            ]

            popular_search = {
                "query": query,
                "search_count": search_count,
                "last_searched": last_searched,
                "trending_score": round(trending_score, 2),
                "category": category,
                "suggestions": suggestions[:3],  # Top 3 suggestions
            }

            popular_searches.append(popular_search)

        # Index popular searches
        actions = []
        for i, search in enumerate(popular_searches):
            action = {"_index": "popular_searches", "_id": i + 1, "_source": search}
            actions.append(action)

        if actions:
            helpers.bulk(self.es, actions)
            self.es.indices.refresh(index="popular_searches")
            print(f"Popular searches indexed successfully: {len(popular_searches)} records")

    def generate_user_sessions(self, users: List[Dict[str, Any]]):
        """Generate user session data."""
        print("Generating user sessions...")
        
        if self.append_mode:
            # Check if session data already exists
            try:
                count = self.es.count(index="user_sessions")["count"]
                if count > 0:
                    print(f"User sessions data skipped: {count} records already exist")
                    return
            except:
                # Index might not exist yet, continue
                pass

        sessions = []
        devices = [
            {"type": "desktop", "os": "Windows 10", "browser": "Chrome", "screen_resolution": "1920x1080"},
            {"type": "desktop", "os": "macOS", "browser": "Safari", "screen_resolution": "2560x1440"},
            {"type": "mobile", "os": "iOS", "browser": "Safari Mobile", "screen_resolution": "375x812"},
            {"type": "mobile", "os": "Android", "browser": "Chrome Mobile", "screen_resolution": "412x915"},
            {"type": "tablet", "os": "iPadOS", "browser": "Safari", "screen_resolution": "1024x768"},
        ]
        
        pages = [
            "/", "/products", "/categories/electronics", "/categories/clothing", 
            "/product/laptop", "/product/smartphone", "/cart", "/checkout",
            "/account", "/search", "/deals", "/support"
        ]

        # Generate sessions for the last 30 days
        for i in range(2000):  # 2000 sessions
            user = random.choice(users)
            session_start = fake.date_time_between(start_date="-30d", end_date="now")
            duration_minutes = random.randint(2, 60)
            session_end = session_start + timedelta(minutes=duration_minutes)
            
            # Generate page views
            num_pages = random.randint(2, 15)
            page_views = []
            current_time = session_start
            
            for _ in range(num_pages):
                page_views.append({
                    "url": random.choice(pages),
                    "timestamp": current_time,
                    "time_spent_seconds": random.randint(10, 300)
                })
                current_time += timedelta(seconds=random.randint(30, 180))
            
            session = {
                "session_id": f"session_{user['id']}_{i}",
                "user_id": user["id"],
                "start_time": session_start,
                "end_time": session_end,
                "duration_minutes": duration_minutes,
                "pages_viewed": page_views,
                "device_info": random.choice(devices),
                "location": {
                    "country": fake.country(),
                    "city": fake.city(),
                    "ip_address": fake.ipv4()
                },
                "referrer": random.choice(["direct", "google.com", "facebook.com", "instagram.com", "email", "bing.com"]),
                "is_active": False,
                "created_at": session_start,
                "updated_at": session_end
            }
            
            sessions.append(session)

        # Bulk index sessions
        actions = []
        for session in sessions:
            action = {"_index": "user_sessions", "_source": session}
            actions.append(action)

        if actions:
            helpers.bulk(self.es, actions, chunk_size=100)
            self.es.indices.refresh(index="user_sessions")
            print(f"User sessions indexed successfully: {len(sessions)} records")

    def generate_user_behavior(self, users: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Generate user behavior events."""
        print("Generating user behavior events...")
        
        if self.append_mode:
            # Check if behavior data already exists
            try:
                count = self.es.count(index="user_behavior")["count"]
                if count > 0:
                    print(f"User behavior data skipped: {count} records already exist")
                    return
            except:
                # Index might not exist yet, continue
                pass

        behaviors = []
        event_types = ["page_view", "product_view", "add_to_cart", "purchase", "search"]
        
        devices = [
            {"type": "desktop", "os": "Windows", "browser": "Chrome"},
            {"type": "mobile", "os": "iOS", "browser": "Safari"},
            {"type": "mobile", "os": "Android", "browser": "Chrome"},
            {"type": "tablet", "os": "iPadOS", "browser": "Safari"},
        ]
        
        search_queries = [
            "laptop", "gaming laptop", "smartphone", "iphone", "headphones",
            "shoes", "running shoes", "dress", "summer clothes", "book",
            "coffee maker", "kitchen appliances", "camera", "dslr camera"
        ]
        
        # Generate behavior events for the last 30 days
        for i in range(10000):  # 10000 events
            user = random.choice(users)
            event_type = random.choice(event_types)
            timestamp = fake.date_time_between(start_date="-30d", end_date="now")
            
            behavior = {
                "user_id": user["id"],
                "session_id": f"session_{user['id']}_{random.randint(1, 100)}",
                "event_type": event_type,
                "timestamp": timestamp,
                "page_url": f"/{random.choice(['', 'products/', 'categories/', 'product/', 'search/', 'cart/', 'checkout/'])}{random.choice(['', 'electronics', 'clothing', 'books', 'home'])}",
                "device_info": random.choice(devices)
            }
            
            # Add event-specific data
            if event_type in ["product_view", "add_to_cart"]:
                behavior["product_id"] = random.choice(products)["id"]
            
            if event_type == "search":
                behavior["search_query"] = random.choice(search_queries)
                if random.random() < 0.4:  # 40% of searches have filters
                    behavior["filters"] = {
                        "category": random.choice(["Electronics", "Clothing", "Books", "Home & Garden", "Sports"]),
                        "price_range": random.choice(["Under $25", "$25-$50", "$50-$100", "Over $100"]),
                        "brand": random.choice(["TechCorp", "StyleBrand", "HomeEssentials", "SportsPro"])
                    }
            
            if event_type == "purchase":
                behavior["order_total"] = round(random.uniform(20, 500), 2)
                behavior["items_count"] = random.randint(1, 5)
            
            behaviors.append(behavior)

        # Bulk index behaviors
        actions = []
        for behavior in behaviors:
            action = {"_index": "user_behavior", "_source": behavior}
            actions.append(action)

        if actions:
            helpers.bulk(self.es, actions, chunk_size=500)
            self.es.indices.refresh(index="user_behavior")
            print(f"User behavior events indexed successfully: {len(behaviors)} records")

    def generate_analytics(self, products: List[Dict[str, Any]]):
        """Generate analytics data."""
        print("Generating analytics data...")
        
        if self.append_mode:
            # Check if analytics data already exists
            try:
                count = self.es.count(index="analytics")["count"]
                if count > 0:
                    print(f"Analytics data skipped: {count} records already exist")
                    return
            except:
                # Index might not exist yet, continue
                pass

        analytics = []
        metric_types = ["daily", "weekly", "monthly"]
        categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports"]
        
        # Generate analytics for the last 90 days
        start_date = datetime.now() - timedelta(days=90)
        
        for metric_type in metric_types:
            if metric_type == "daily":
                num_records = 90
                days_per_record = 1
            elif metric_type == "weekly":
                num_records = 13
                days_per_record = 7
            else:  # monthly
                num_records = 3
                days_per_record = 30
            
            for i in range(num_records):
                record_date = start_date + timedelta(days=i * days_per_record)
                
                # Generate realistic metrics
                base_visitors = random.randint(5000, 20000)
                unique_visitors = base_visitors
                returning_visitors = int(base_visitors * random.uniform(0.3, 0.5))
                new_visitors = unique_visitors - returning_visitors
                
                page_views = int(unique_visitors * random.uniform(3, 6))
                sessions = int(unique_visitors * random.uniform(1.2, 1.8))
                bounce_rate = random.uniform(0.3, 0.6)
                avg_session_duration = random.uniform(2.5, 8.5)  # minutes
                
                conversion_rate = random.uniform(0.01, 0.05)
                orders = int(unique_visitors * conversion_rate)
                avg_order_value = random.uniform(50, 150)
                revenue = orders * avg_order_value
                
                # Top products
                top_products = []
                selected_products = random.sample(products, min(5, len(products)))
                for product in selected_products:
                    top_products.append({
                        "product_id": product["id"],
                        "name": product["name"],
                        "views": random.randint(100, 1000),
                        "sales": random.randint(10, 100)
                    })
                
                # Top categories
                top_categories = []
                for category in random.sample(categories, 3):
                    top_categories.append({
                        "category": category,
                        "views": random.randint(500, 5000),
                        "sales": random.randint(50, 500)
                    })
                
                # Traffic sources (should sum to 100)
                direct = random.randint(20, 40)
                search = random.randint(20, 40)
                social = random.randint(10, 30)
                referral = 100 - direct - search - social
                
                # Device breakdown (should sum to 100)
                desktop = random.randint(40, 60)
                mobile = random.randint(30, 50)
                tablet = 100 - desktop - mobile
                
                analytic = {
                    "date": record_date,
                    "metric_type": metric_type,
                    "unique_visitors": unique_visitors,
                    "returning_visitors": returning_visitors,
                    "new_visitors": new_visitors,
                    "page_views": page_views,
                    "sessions": sessions,
                    "bounce_rate": bounce_rate,
                    "avg_session_duration": avg_session_duration,
                    "conversion_rate": conversion_rate,
                    "revenue": revenue,
                    "orders": orders,
                    "avg_order_value": avg_order_value,
                    "top_products": top_products,
                    "top_categories": top_categories,
                    "traffic_sources": {
                        "direct": direct,
                        "search": search,
                        "social": social,
                        "referral": referral
                    },
                    "device_breakdown": {
                        "desktop": desktop,
                        "mobile": mobile,
                        "tablet": tablet
                    }
                }
                
                analytics.append(analytic)

        # Bulk index analytics
        actions = []
        for analytic in analytics:
            action = {"_index": "analytics", "_source": analytic}
            actions.append(action)

        if actions:
            helpers.bulk(self.es, actions, chunk_size=100)
            self.es.indices.refresh(index="analytics")
            print(f"Analytics data indexed successfully: {len(analytics)} records")

    def populate_database(self):
        """Main method to populate Elasticsearch with all data."""
        mode_text = "append mode" if self.append_mode else "recreate mode"
        print(f"Starting Elasticsearch database population ({mode_text})...")

        # Wait for Elasticsearch to be ready
        self.wait_for_elasticsearch()

        # Load data from shared_data directory
        data_dir = os.path.join("..", "..", "shared_data")

        # Check if all required data files exist
        required_files = ["products.json", "users.json"]
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

        # Create indices and populate
        self.create_indices()
        self.index_products(data["products"])
        self.generate_search_analytics(data["users"], data["products"])
        self.generate_popular_searches()
        
        # Generate data for migrated indices
        self.generate_user_sessions(data["users"])
        self.generate_user_behavior(data["users"], data["products"])
        self.generate_analytics(data["products"])

        print("Elasticsearch database population completed successfully!")

        # Print summary
        indices = ["products", "search_analytics", "popular_searches", "user_sessions", "user_behavior", "analytics"]
        for index in indices:
            try:
                count = self.es.count(index=index)["count"]
                print(f"{index}: {count} documents")
            except Exception as e:
                print(f"Error counting documents in {index}: {e}")


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Populate Elasticsearch database with e-commerce data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python populate_data.py                 # Recreate indices (default)
    python populate_data.py --recreate      # Recreate indices explicitly  
    python populate_data.py --append        # Add to existing indices
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--recreate", 
        action="store_true", 
        default=True,
        help="Drop and recreate indices, overwriting all data (default)"
    )
    mode_group.add_argument(
        "--append", 
        action="store_true",
        help="Add new data to existing indices, preserving existing documents"
    )
    
    args = parser.parse_args()
    
    # Determine mode
    append_mode = args.append
    
    if append_mode:
        print("🔄 Running in APPEND mode - existing data will be preserved")
    else:
        print("🔄 Running in RECREATE mode - indices will be recreated")
        print("⚠️  WARNING: This will destroy all existing data!")
        
    try:
        populator = ElasticsearchPopulator(append_mode=append_mode)
        populator.populate_database()
        
        if append_mode:
            print("✅ Database append completed successfully!")
        else:
            print("✅ Database recreation completed successfully!")
            
    except Exception as e:
        print(f"❌ Error populating Elasticsearch database: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
