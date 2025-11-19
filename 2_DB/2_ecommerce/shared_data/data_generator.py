"""
Main data generation orchestrator for the multi-database e-commerce project.
This module creates consistent, realistic data using modular generators.
"""

import os
from typing import Dict, Any, List
from faker import Faker

from generators.base_generator import BaseGenerator
from generators.content_generator import ContentGenerator
from generators.image_generator import ImageGenerator
from generators.product_generator import ProductGenerator
from generators.user_generator import UserGenerator
from generators.order_generator import OrderGenerator
from generators.review_generator import ReviewGenerator


class DataGenerator(BaseGenerator):
    """Main data generator that orchestrates all component generators."""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        minio_endpoint: str = "localhost:9000",
        minio_access_key: str = "admin",
        minio_secret_key: str = "password123",
    ):
        super().__init__()

        # Initialize component generators
        self.content_generator = ContentGenerator(use_llm=True, ollama_host=ollama_host)

        self.image_generator = ImageGenerator(
            minio_endpoint=minio_endpoint,
            minio_access_key=minio_access_key,
            minio_secret_key=minio_secret_key,
        )

        self.product_generator = ProductGenerator(
            content_generator=self.content_generator,
            image_generator=self.image_generator,
        )

        self.user_generator = UserGenerator()
        self.order_generator = OrderGenerator()
        self.review_generator = ReviewGenerator(
            content_generator=self.content_generator
        )

        # Store generated data
        self.products = []
        self.users = []
        self.orders = []
        self.reviews = []

    def generate_all_data(
        self,
        num_products: int = 1000,
        num_users: int = 500,
        orders_per_user_range: tuple = (0, 10),
        reviews_per_product_range: tuple = (0, 20),
        output_dir: str = None,
    ) -> Dict[str, Any]:
        """Generate all data types and save to files."""

        print("🚀 Starting comprehensive data generation...")

        # Safety check: warn if existing data files would be overwritten
        import os

        existing_files = []
        files_to_check = ["products.json", "users.json", "orders.json", "reviews.json"]

        if output_dir is None:
            if os.path.basename(os.getcwd()) == "shared_data":
                check_dir = "."
            else:
                check_dir = "shared_data"
        else:
            check_dir = output_dir

        for filename in files_to_check:
            filepath = os.path.join(check_dir, filename)
            if os.path.exists(filepath):
                existing_files.append(filename)

        if existing_files:
            print(f"\n⚠️  WARNING: The following existing files will be OVERWRITTEN:")
            for filename in existing_files:
                filepath = os.path.join(check_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        import json

                        data = json.load(f)
                        print(f"   • {filename} ({len(data)} existing records)")
                except:
                    print(f"   • {filename} (existing file)")
            print(f"\n💡 If you want to ADD to existing data instead of replacing it,")
            print(f"   use the --enhance flag or call enhance_existing_data() method.")
            print(f"\n⏳ Continuing in 3 seconds... (Press Ctrl+C to cancel)")

            import time

            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print(f"\n❌ Generation cancelled by user.")
                return {}

        print(f"\n📁 Output directory: {check_dir}")

        # Generate products
        print(f"\n📦 Generating {num_products} products...")
        self.products = self.product_generator.generate_products(num_products)
        products_file = self.save_to_json_file(
            self.products, "products.json", output_dir
        )

        # Generate users
        print(f"\n👥 Generating {num_users} users...")
        self.users = self.user_generator.generate_users(num_users)
        users_file = self.save_to_json_file(self.users, "users.json", output_dir)

        # Generate orders
        print(f"\n🛒 Generating orders for users...")
        self.orders = self.order_generator.generate_orders(
            self.users, self.products, orders_per_user_range
        )
        orders_file = self.save_to_json_file(self.orders, "orders.json", output_dir)

        # Generate reviews
        print(f"\n⭐ Generating reviews for products...")
        self.reviews = self.review_generator.generate_reviews_for_products(
            self.products, self.users, self.orders, reviews_per_product_range
        )
        reviews_file = self.save_to_json_file(self.reviews, "reviews.json", output_dir)

        # Generate metadata
        metadata = self.generate_metadata(
            {
                "products": len(self.products),
                "users": len(self.users),
                "orders": len(self.orders),
                "reviews": len(self.reviews),
            },
            {
                "num_products": num_products,
                "num_users": num_users,
                "orders_per_user_range": orders_per_user_range,
                "reviews_per_product_range": reviews_per_product_range,
                "use_llm": True,
                "use_stable_diffusion": True,
                "use_minio": True,
            },
        )
        metadata_file = self.save_to_json_file([metadata], "metadata.json", output_dir)

        print(f"\n✅ Data generation complete!")
        print(f"📊 Generated:")
        print(f"   • {len(self.products)} products")
        print(f"   • {len(self.users)} users")
        print(f"   • {len(self.orders)} orders")
        print(f"   • {len(self.reviews)} reviews")

        return {
            "products": self.products,
            "users": self.users,
            "orders": self.orders,
            "reviews": self.reviews,
            "metadata": metadata,
            "files": {
                "products": products_file,
                "users": users_file,
                "orders": orders_file,
                "reviews": reviews_file,
                "metadata": metadata_file,
            },
        }

    def enhance_existing_data(
        self,
        num_new_products: int = 10,
        num_new_users: int = 5,
        orders_per_user_range: tuple = (0, 5),
        reviews_per_product_range: tuple = (0, 10),
        output_dir: str = None,
    ) -> Dict[str, Any]:
        """Enhance existing data files by adding new records."""

        print("🔧 Starting data enhancement...")

        # Load existing data
        print("\n📂 Loading existing data...")
        existing_products = self.load_existing_json_file("products.json", output_dir)
        existing_users = self.load_existing_json_file("users.json", output_dir)
        existing_orders = self.load_existing_json_file("orders.json", output_dir)
        existing_reviews = self.load_existing_json_file("reviews.json", output_dir)

        # Get next available IDs
        next_product_id = self.get_next_id(existing_products)
        next_user_id = self.get_next_id(existing_users)
        next_order_id = self.get_next_id(existing_orders)
        next_review_id = self.get_next_id(existing_reviews)

        print(f"📊 Current data counts:")
        print(f"   • Products: {len(existing_products)} (next ID: {next_product_id})")
        print(f"   • Users: {len(existing_users)} (next ID: {next_user_id})")
        print(f"   • Orders: {len(existing_orders)} (next ID: {next_order_id})")
        print(f"   • Reviews: {len(existing_reviews)} (next ID: {next_review_id})")

        # Generate new products
        print(f"\n📦 Generating {num_new_products} new products...")
        new_products = self.product_generator.generate_products(
            num_new_products, starting_id=next_product_id
        )

        # Generate new users
        print(f"\n👥 Generating {num_new_users} new users...")
        new_users = self.user_generator.generate_users(
            num_new_users, starting_id=next_user_id
        )

        # Combine existing and new data for order generation
        all_products = existing_products + new_products
        all_users = existing_users + new_users

        # Generate new orders (for new users only)
        print(f"\n🛒 Generating orders for new users...")
        new_orders = self.order_generator.generate_orders(
            new_users, all_products, orders_per_user_range, starting_id=next_order_id
        )

        # Generate new reviews (for new products only)
        print(f"\n⭐ Generating reviews for new products...")
        new_reviews = self.review_generator.generate_reviews_for_products(
            new_products,
            all_users,
            existing_orders + new_orders,
            reviews_per_product_range,
            starting_id=next_review_id,
        )

        # Save enhanced data
        products_file = self.merge_and_save_json_file(
            new_products, existing_products, "products.json", output_dir
        )
        users_file = self.merge_and_save_json_file(
            new_users, existing_users, "users.json", output_dir
        )
        orders_file = self.merge_and_save_json_file(
            new_orders, existing_orders, "orders.json", output_dir
        )
        reviews_file = self.merge_and_save_json_file(
            new_reviews, existing_reviews, "reviews.json", output_dir
        )

        # Update stored data for metadata
        self.products = existing_products + new_products
        self.users = existing_users + new_users
        self.orders = existing_orders + new_orders
        self.reviews = existing_reviews + new_reviews

        # Generate metadata
        metadata = self.generate_metadata(
            {
                "products": len(self.products),
                "users": len(self.users),
                "orders": len(self.orders),
                "reviews": len(self.reviews),
                "new_products": len(new_products),
                "new_users": len(new_users),
                "new_orders": len(new_orders),
                "new_reviews": len(new_reviews),
            },
            {
                "mode": "enhance",
                "num_new_products": num_new_products,
                "num_new_users": num_new_users,
                "orders_per_user_range": orders_per_user_range,
                "reviews_per_product_range": reviews_per_product_range,
                "use_llm": True,
                "use_stable_diffusion": True,
                "use_minio": True,
            },
        )
        metadata_file = self.save_to_json_file([metadata], "metadata.json", output_dir)

        print(f"\n✅ Data enhancement complete!")
        print(f"📊 Final totals:")
        print(f"   • {len(self.products)} products (+{len(new_products)} new)")
        print(f"   • {len(self.users)} users (+{len(new_users)} new)")
        print(f"   • {len(self.orders)} orders (+{len(new_orders)} new)")
        print(f"   • {len(self.reviews)} reviews (+{len(new_reviews)} new)")

        return {
            "products": self.products,
            "users": self.users,
            "orders": self.orders,
            "reviews": self.reviews,
            "metadata": metadata,
            "new_data": {
                "products": new_products,
                "users": new_users,
                "orders": new_orders,
                "reviews": new_reviews,
            },
            "files": {
                "products": products_file,
                "users": users_file,
                "orders": orders_file,
                "reviews": reviews_file,
                "metadata": metadata_file,
            },
        }


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate e-commerce data")
    parser.add_argument(
        "--products",
        type=int,
        default=30,
        help="Number of products to generate (or add if using --enhance)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Number of users to generate (or add if using --enhance)",
    )
    parser.add_argument(
        "--output-dir", type=str, help="Output directory for generated files"
    )
    parser.add_argument(
        "--enhance",
        action="store_true",
        help="Enhance existing data files instead of replacing them",
    )

    args = parser.parse_args()

    generator = DataGenerator()

    if args.enhance:
        generator.enhance_existing_data(
            num_new_products=args.products,
            num_new_users=args.users,
            output_dir=args.output_dir,
        )
    else:
        generator.generate_all_data(
            num_products=args.products, num_users=args.users, output_dir=args.output_dir
        )


if __name__ == "__main__":
    main()
