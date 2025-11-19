"""
Qdrant database population script for e-commerce data.
Handles vector embeddings for AI-powered product recommendations and semantic search.

Usage:
    python populate_data.py [--recreate|--append]

Modes:
    --recreate (default): Drop and recreate collections, overwriting all data
    --append: Add new data to existing collections, preserving existing vectors
"""

import json
import sys
import os
import argparse
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

# Add shared_data to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class QdrantPopulator:
    """Populates Qdrant with e-commerce vector embeddings."""
    
    def __init__(self, append_mode: bool = False):
        # Connect to Qdrant
        self.client = QdrantClient(
            host="localhost",
            port=6333
        )
        self.append_mode = append_mode
        
        # Initialize embedding model
        print("🤖 Loading SentenceTransformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded successfully")
        
        # Collection names
        self.product_collection = "product_embeddings"
        self.user_collection = "user_preference_embeddings"
        
    def create_collections(self):
        """Create Qdrant collections for embeddings."""
        if self.append_mode:
            print("Append mode: Ensuring collections exist...")
        else:
            print("Recreate mode: Creating fresh collections...")
        
        # Get embedding dimension
        sample_text = "sample text for dimension calculation"
        sample_embedding = self.model.encode([sample_text])
        vector_size = len(sample_embedding[0])
        print(f"Vector dimension: {vector_size}")
        
        # Handle product collection
        if self.append_mode:
            # Check if collection exists
            try:
                info = self.client.get_collection(self.product_collection)
                print(f"Product collection already exists with {info.points_count} points")
            except:
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=self.product_collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created product collection: {self.product_collection}")
        else:
            # Recreate mode - delete and create fresh
            try:
                self.client.delete_collection(self.product_collection)
                print(f"Dropped existing product collection: {self.product_collection}")
            except:
                pass  # Collection might not exist
                
            self.client.create_collection(
                collection_name=self.product_collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Created product collection: {self.product_collection}")
        
        # Handle user preference collection
        if self.append_mode:
            # Check if collection exists
            try:
                info = self.client.get_collection(self.user_collection)
                print(f"User collection already exists with {info.points_count} points")
            except:
                # Collection doesn't exist, create it
                self.client.create_collection(
                    collection_name=self.user_collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created user collection: {self.user_collection}")
        else:
            # Recreate mode - delete and create fresh
            try:
                self.client.delete_collection(self.user_collection)
                print(f"Dropped existing user collection: {self.user_collection}")
            except:
                pass  # Collection might not exist
                
            self.client.create_collection(
                collection_name=self.user_collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"Created user collection: {self.user_collection}")
        
        print("✓ Collections setup completed successfully")
    
    def generate_product_embedding_text(self, product: Dict[str, Any]) -> str:
        """Generate comprehensive text representation for product embedding."""
        # Core product information
        text_parts = [
            product['name'],
            product['description'],
            product['category'],
            product['brand']
        ]
        
        # Add features if available
        features = product.get('features', {})
        if features:
            feature_text = " ".join([f"{k}: {v}" for k, v in features.items() if v])
            if feature_text:
                text_parts.append(feature_text)
        
        # Add tags
        tags = product.get('tags', [])
        if tags:
            text_parts.append(" ".join(tags))
        
        return " ".join(text_parts)
    
    def insert_product_embeddings(self, products: List[Dict[str, Any]]):
        """Generate and insert product embeddings with content/metadata structure."""
        print(f"Generating embeddings for {len(products)} products...")
        
        # Filter out existing products in append mode
        products_to_process = []
        skipped_count = 0
        
        if self.append_mode:
            print("Checking for existing products...")
            for product in products:
                try:
                    # Check if point exists
                    existing = self.client.retrieve(
                        collection_name=self.product_collection,
                        ids=[int(product["id"])]
                    )
                    if existing:
                        skipped_count += 1
                        continue
                except:
                    # Point doesn't exist, include it
                    pass
                products_to_process.append(product)
        else:
            products_to_process = products
        
        if not products_to_process:
            if self.append_mode:
                print(f"All {len(products)} products already exist - skipping")
            return
        
        print(f"Processing {len(products_to_process)} products ({skipped_count} skipped)")
        
        # Prepare data with content/metadata structure
        product_data = []
        
        for i, product in enumerate(products_to_process):
            # Generate content text for embedding
            content = self.generate_product_embedding_text(product)
            
            # Prepare metadata
            metadata = {
                "id": str(product["id"]),
                "name": product["name"],
                "description": product["description"],
                "category": product["category"],
                "brand": product["brand"],
                "price": float(product["price"]),
                "rating": float(product["rating"]),
                "in_stock": product["in_stock"],
                "sku": product.get("sku"),
                "tags": product.get("tags", [])[:10],  # Limit tags to avoid payload size issues
            }
            
            # Add key features to metadata
            features = product.get("features", {})
            if features:
                metadata["features"] = features
            
            product_data.append({
                "content": content,
                "metadata": metadata
            })
            
            if i % 100 == 0:
                print(f"Prepared {i} products for embedding...")
        
        # Extract content for embedding generation
        texts = [item["content"] for item in product_data]
        
        # Generate embeddings in batches
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch_texts, show_progress_bar=True)
            all_embeddings.extend(batch_embeddings)
            print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        # Create points for insertion
        points = []
        for item, embedding in zip(product_data, all_embeddings):
            point = PointStruct(
                id=int(item["metadata"]["id"]),
                vector=embedding.tolist(),
                payload={
                    "content": item["content"],  # Store the full content text
                    "metadata": item["metadata"]
                }
            )
            points.append(point)
        
        # Insert points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch_points = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.product_collection,
                points=batch_points
            )
            print(f"Inserted batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
        
        if self.append_mode:
            print(f"✓ Product embeddings processed: {len(points)} inserted, {skipped_count} skipped")
        else:
            print(f"✓ Product embeddings inserted successfully: {len(points)}")
    
    def generate_user_embedding_text(self, user: Dict[str, Any], orders: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> str:
        """Generate user preference text from their behavior and preferences."""
        text_parts = []
        
        # Add explicit preferences
        preferences = user.get('preferences', {})
        if 'preferred_categories' in preferences:
            text_parts.extend(preferences['preferred_categories'])
        
        # Add purchase history patterns
        user_orders = [order for order in orders if order['user_id'] == user['id']]
        
        # Extract purchased product categories and names
        purchased_categories = []
        purchased_products = []
        
        for order in user_orders:
            for item in order.get('items', []):
                # Find the product
                product = next((p for p in products if p['id'] == item['product_id']), None)
                if product:
                    purchased_categories.append(product['category'])
                    purchased_products.append(product['name'])
        
        # Add most common categories
        if purchased_categories:
            from collections import Counter
            common_categories = Counter(purchased_categories).most_common(3)
            text_parts.extend([cat for cat, _ in common_categories])
        
        # Add some purchased product names (limited)
        if purchased_products:
            text_parts.extend(purchased_products[:5])
        
        # Add user demographics that might affect preferences
        if user.get('gender'):
            text_parts.append(user['gender'])
        
        # Add loyalty level based on stats
        stats = user.get('stats', {})
        if stats.get('total_spent', 0) > 1000:
            text_parts.append("premium customer high spending")
        elif stats.get('orders_count', 0) > 10:
            text_parts.append("frequent buyer loyal customer")
        
        return " ".join(text_parts) if text_parts else "general customer"
    
    def insert_user_embeddings(self, users: List[Dict[str, Any]], orders: List[Dict[str, Any]], products: List[Dict[str, Any]]):
        """Generate and insert user preference embeddings with content/metadata structure."""
        print(f"Generating user preference embeddings for {len(users)} users...")
        
        # Filter out existing users in append mode
        users_to_process = []
        skipped_count = 0
        
        if self.append_mode:
            print("Checking for existing users...")
            for user in users:
                try:
                    # Check if point exists
                    existing = self.client.retrieve(
                        collection_name=self.user_collection,
                        ids=[int(user["id"])]
                    )
                    if existing:
                        skipped_count += 1
                        continue
                except:
                    # Point doesn't exist, include it
                    pass
                users_to_process.append(user)
        else:
            users_to_process = users
        
        if not users_to_process:
            if self.append_mode:
                print(f"All {len(users)} users already exist - skipping")
            return
        
        print(f"Processing {len(users_to_process)} users ({skipped_count} skipped)")
        
        # Prepare data with content/metadata structure
        user_data = []
        
        for user in users_to_process:
            # Generate content text for embedding
            content = self.generate_user_embedding_text(user, orders, products)
            
            # Calculate user behavior metrics
            user_orders = [order for order in orders if order['user_id'] == user['id']]
            
            # Get category preferences from purchase history
            purchased_categories = []
            total_spent_by_category = {}
            
            for order in user_orders:
                for item in order.get('items', []):
                    product = next((p for p in products if p['id'] == item['product_id']), None)
                    if product:
                        category = product['category']
                        purchased_categories.append(category)
                        total_spent_by_category[category] = total_spent_by_category.get(category, 0) + item.get('total_price', 0)
            
            # Prepare metadata
            metadata = {
                "id": str(user["id"]),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_premium": user.get("is_premium", False),
                "preferred_categories": user.get("preferences", {}).get("preferred_categories", []),
                "total_orders": user.get("stats", {}).get("orders_count", 0),
                "total_spent": float(user.get("stats", {}).get("total_spent", 0)),
                "avg_order_value": float(user.get("stats", {}).get("average_order_value", 0)),
                "top_category": max(total_spent_by_category.items(), key=lambda x: x[1])[0] if total_spent_by_category else None,
                "language": user.get("preferences", {}).get("language"),
                "currency": user.get("preferences", {}).get("currency")
            }
            
            user_data.append({
                "content": content,
                "metadata": metadata
            })
        
        # Extract content for embedding generation
        texts = [item["content"] for item in user_data]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} user texts...")
        for i, text in enumerate(texts[:3]):  # Debug first 3 texts
            print(f"  User {i+1} text: '{text}' (length: {len(text)})")
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"Generated {len(embeddings)} embeddings")
        
        # Create points
        points = []
        for i, (item, embedding) in enumerate(zip(user_data, embeddings)):
            user_id = int(item["metadata"]["id"])
            
            # Debug embedding info
            if i < 3:  # Debug first 3 embeddings
                print(f"  User {user_id}: embedding type={type(embedding)}, shape={getattr(embedding, 'shape', 'no shape')}")
                if hasattr(embedding, 'tolist'):
                    try:
                        vector_list = embedding.tolist()
                        print(f"    Vector list length: {len(vector_list) if vector_list else 'None'}")
                    except Exception as e:
                        print(f"    Error converting to list: {e}")
                        vector_list = None
                else:
                    print(f"    No tolist() method available")
                    vector_list = None
            else:
                vector_list = embedding.tolist() if hasattr(embedding, 'tolist') else None
            
            point = PointStruct(
                id=user_id,
                vector=vector_list,
                payload={
                    "content": item["content"],  # Store the full content text
                    "metadata": item["metadata"]
                }
            )
            points.append(point)
        
        # Insert points
        self.client.upsert(
            collection_name=self.user_collection,
            points=points
        )
        
        if self.append_mode:
            print(f"✓ User embeddings processed: {len(points)} inserted, {skipped_count} skipped")
        else:
            print(f"✓ User embeddings inserted successfully: {len(points)}")
    
    def create_indexes(self):
        """Create any additional indexes or optimizations."""
        print("Optimizing collections...")
        
        # The indexes are automatically created by Qdrant for vector search
        # We can create payload indexes for faster filtering
        
        # Index for product metadata (adjust for new structure)
        try:
            self.client.create_payload_index(
                collection_name=self.product_collection,
                field_name="metadata.category"
            )
            self.client.create_payload_index(
                collection_name=self.product_collection,
                field_name="metadata.price"
            )
            self.client.create_payload_index(
                collection_name=self.product_collection,
                field_name="metadata.in_stock"
            )
            self.client.create_payload_index(
                collection_name=self.product_collection,
                field_name="metadata.brand"
            )
        except Exception as e:
            print(f"Note: Some indexes may already exist: {e}")
        
        print("✓ Optimization complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get database status and collection info."""
        try:
            collections = self.client.get_collections()
            
            product_info = self.client.get_collection(self.product_collection)
            user_info = self.client.get_collection(self.user_collection)
            
            return {
                "status": "healthy",
                "collections": {
                    "product_embeddings": {
                        "points_count": product_info.points_count,
                        "vector_size": product_info.config.params.vectors.size
                    },
                    "user_preference_embeddings": {
                        "points_count": user_info.points_count,
                        "vector_size": user_info.config.params.vectors.size
                    }
                },
                "total_collections": len(collections.collections)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


def load_json_data(filename: str) -> List[Dict[str, Any]]:
    """Load data from JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'shared_data', filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Error: {filename} not found at {filepath}")
        print("Please run the data generator first:")
        print("cd shared_data && uv run data_generator.py")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        return json.load(f)


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Populate Qdrant database with e-commerce data",
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
        help="Add new data to existing collections, preserving existing vectors"
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
        mode_text = "append mode" if append_mode else "recreate mode"
        print(f"🚀 Starting Qdrant database population ({mode_text})...")
        
        # Load data
        print("📂 Loading data files...")
        products = load_json_data('products.json')
        users = load_json_data('users.json')
        orders = load_json_data('orders.json')
        
        print(f"✓ Loaded {len(products)} products, {len(users)} users, {len(orders)} orders")
        
        # Initialize populator
        populator = QdrantPopulator(append_mode=append_mode)
        
        # Create collections
        populator.create_collections()
        
        # Insert data
        populator.insert_product_embeddings(products)
        populator.insert_user_embeddings(users, orders, products)
        
        # Optimize
        populator.create_indexes()
        
        # Show final status
        print("\n📊 Final Status:")
        status = populator.get_status()
        print(json.dumps(status, indent=2))
        
        if append_mode:
            print("\n✅ Database append completed successfully!")
        else:
            print("\n✅ Database recreation completed successfully!")
        print("🔗 API will be available at: http://localhost:8004")
        print("🎯 Vector similarity search and recommendations are ready!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error populating Qdrant database: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())