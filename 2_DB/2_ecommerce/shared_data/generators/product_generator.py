"""
Product generation functionality.
Handles product creation with features, pricing, and categories.
"""

import random
from typing import Dict, Any, List
from faker import Faker

from .base_generator import BaseGenerator
from .product_data import PRODUCT_CATEGORIES
from .content_generator import ContentGenerator
from .image_generator import ImageGenerator


class ProductGenerator(BaseGenerator):
    """Handles product generation with realistic data."""

    def __init__(
        self,
        content_generator: ContentGenerator = None,
        image_generator: ImageGenerator = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.content_generator = content_generator or ContentGenerator()
        self.image_generator = image_generator or ImageGenerator()

        # Brand pools for different categories
        self.brands = {
            "Electronics": [
                "TechPro",
                "DigitalMax",
                "InnovateTech",
                "FutureTech",
                "SmartLine",
                "ProGear",
                "NextGen",
                "TechCraft",
                "DigitalEdge",
                "InnoCore",
            ],
            "Clothing": [
                "StyleCraft",
                "UrbanWear",
                "FashionForward",
                "TrendSetter",
                "ModernFit",
                "ClassicStyle",
                "StreetWear",
                "ElegantLine",
                "CasualPlus",
                "ActiveWear",
            ],
            "Books": [
                "LearningPress",
                "WisdomBooks",
                "KnowledgeHub",
                "BookCraft",
                "ScholarPress",
                "InsightPublishing",
                "ThoughtWorks",
                "BrightMinds",
                "DeepThought",
                "ClearPath",
            ],
            "Home & Garden": [
                "HomeCraft",
                "LivingSpace",
                "GardenPro",
                "HomeEssentials",
                "ComfortZone",
                "QualityHome",
                "PracticalLiving",
                "HomeStyle",
                "EverydayLiving",
                "LifeSpace",
            ],
            "Sports": [
                "ActiveLife",
                "SportsPro",
                "FitGear",
                "AthleticEdge",
                "PowerSport",
                "EndurancePro",
                "PerformanceGear",
                "SportCraft",
                "FitnessPlus",
                "ActiveZone",
            ],
        }

    def generate_product_features(
        self, category: str, product_type: str
    ) -> Dict[str, Any]:
        """Generate category-specific features for products."""
        features = {}

        if category == "Electronics":
            if any(x in product_type.lower() for x in ["laptop", "computer"]):
                features.update(
                    {
                        "processor": random.choice(
                            ["Intel i5", "Intel i7", "AMD Ryzen 5", "AMD Ryzen 7"]
                        ),
                        "ram": random.choice(["8GB", "16GB", "32GB"]),
                        "storage": random.choice(
                            ["256GB SSD", "512GB SSD", "1TB SSD", "1TB HDD"]
                        ),
                        "screen_size": random.choice(
                            ['13.3"', '14"', '15.6"', '17.3"']
                        ),
                    }
                )
            elif "tablet" in product_type.lower():
                features.update(
                    {
                        "screen_size": random.choice(['8"', '10.1"', '11"', '12.9"']),
                        "storage": random.choice(["64GB", "128GB", "256GB", "512GB"]),
                        "processor": random.choice(
                            ["Apple A14", "Snapdragon 8", "MediaTek Helio"]
                        ),
                        "battery": random.choice(["6000mAh", "7000mAh", "8000mAh"]),
                    }
                )
            elif any(x in product_type.lower() for x in ["phone", "smartphone"]):
                features.update(
                    {
                        "screen_size": random.choice(['5.5"', '6.1"', '6.4"', '6.7"']),
                        "storage": random.choice(["64GB", "128GB", "256GB", "512GB"]),
                        "camera": random.choice(["12MP", "48MP", "64MP", "108MP"]),
                        "battery": random.choice(["3000mAh", "4000mAh", "5000mAh"]),
                    }
                )
            elif "headphones" in product_type.lower():
                features.update(
                    {
                        "type": random.choice(
                            ["Over-ear", "On-ear", "In-ear", "True Wireless"]
                        ),
                        "noise_cancellation": random.choice([True, False]),
                        "battery_life": random.choice(
                            ["6 hours", "20 hours", "30 hours"]
                        ),
                        "connectivity": random.choice(
                            ["Bluetooth 5.0", "Wired", "Bluetooth 5.2"]
                        ),
                    }
                )
            else:
                # Default features for other electronics (camera, monitor, keyboard, mouse, speaker, smartwatch)
                features.update(
                    {
                        "power": random.choice(
                            ["Battery", "AC Power", "USB-C", "USB Rechargeable"]
                        ),
                        "warranty": random.choice(["1 year", "2 years", "3 years"]),
                        "connectivity": random.choice(
                            ["Wireless", "Wired", "Bluetooth", "USB"]
                        ),
                    }
                )

        elif category == "Clothing":
            features.update(
                {
                    "size": random.choice(["XS", "S", "M", "L", "XL", "XXL"]),
                    "color": random.choice(
                        ["Black", "White", "Blue", "Red", "Green", "Gray", "Navy"]
                    ),
                    "material": random.choice(
                        ["Cotton", "Polyester", "Cotton Blend", "Wool", "Denim"]
                    ),
                }
            )

            if any(x in product_type.lower() for x in ["shoes", "sneakers", "boots"]):
                features.update(
                    {
                        "shoe_size": random.choice(
                            ["7", "8", "8.5", "9", "9.5", "10", "11", "12"]
                        ),
                        "width": random.choice(["Regular", "Wide"]),
                    }
                )

        elif category == "Books":
            features.update(
                {
                    "pages": random.randint(150, 800),
                    "format": random.choice(["Paperback", "Hardcover", "E-book"]),
                    "language": "English",
                    "isbn": self.fake.isbn13(),
                }
            )

        elif category == "Home & Garden":
            if "coffee" in product_type.lower():
                features.update(
                    {
                        "capacity": random.choice(["4 cups", "8 cups", "12 cups"]),
                        "type": random.choice(["Drip", "Espresso", "French Press"]),
                    }
                )
            elif "blender" in product_type.lower():
                features.update(
                    {
                        "power": random.choice(["500W", "750W", "1000W", "1200W"]),
                        "capacity": random.choice(["1.5L", "2L", "2.5L"]),
                    }
                )

        elif category == "Sports":
            if "shoes" in product_type.lower():
                features.update(
                    {
                        "shoe_size": random.choice(
                            ["7", "8", "8.5", "9", "9.5", "10", "11", "12"]
                        ),
                        "surface": random.choice(
                            ["Road", "Trail", "Indoor", "All-terrain"]
                        ),
                    }
                )
            elif "dumbbells" in product_type.lower():
                features.update(
                    {
                        "weight": random.choice(
                            ["5 lbs", "10 lbs", "15 lbs", "20 lbs", "25 lbs"]
                        ),
                        "material": random.choice(
                            ["Cast Iron", "Rubber Coated", "Neoprene"]
                        ),
                    }
                )
            else:
                # Default features for other sports equipment
                features.update(
                    {
                        "material": random.choice(
                            ["Rubber", "Leather", "Synthetic", "Nylon"]
                        ),
                        "suitable_for": random.choice(["Indoor", "Outdoor", "Both"]),
                    }
                )

        return features

    def generate_product_price(self, category: str, features: Dict[str, Any]) -> float:
        """Generate realistic price based on category and features."""
        base_prices = {
            "Electronics": (50, 2000),
            "Clothing": (15, 200),
            "Books": (10, 80),
            "Home & Garden": (20, 500),
            "Sports": (25, 300),
        }

        min_price, max_price = base_prices.get(category, (20, 100))
        base_price = random.uniform(min_price, max_price)

        # Adjust price based on features
        if category == "Electronics":
            if "i7" in str(features.get("processor", "")):
                base_price *= 1.3
            if "32GB" in str(features.get("ram", "")):
                base_price *= 1.4
            if "SSD" in str(features.get("storage", "")):
                base_price *= 1.2

        elif category == "Books":
            if features.get("format") == "Hardcover":
                base_price *= 1.5
            elif features.get("format") == "E-book":
                base_price *= 0.6

        # Round to realistic price points
        if base_price < 50:
            return round(base_price * 2) / 2  # Round to nearest $0.50
        else:
            return round(base_price)  # Round to nearest dollar

    def generate_product(self, product_id: int, category: str = None) -> Dict[str, Any]:
        """Generate a single product with all attributes."""
        if category is None:
            category = random.choice(list(PRODUCT_CATEGORIES.keys()))

        product_type = random.choice(PRODUCT_CATEGORIES[category])
        brand = random.choice(self.brands[category])

        # Generate base product name
        product_name = f"{brand} {product_type}"
        if random.random() < 0.3:  # 30% chance of model number
            model = random.choice(["Pro", "Elite", "Max", "Plus", "X", "Ultra"])
            product_name += f" {model}"

        # Generate features
        features = self.generate_product_features(category, product_type)

        # Generate price
        price = self.generate_product_price(category, features)

        # Create product data for content generation
        product_for_content = {
            "name": product_name,
            "category": category,
            "brand": brand,
            "price": price,
            **features,
        }

        # Generate description using content generator
        description = self.content_generator.generate_llm_description(
            product_name, category, brand, features
        )

        # Add description to product data for image generation
        product_for_content["description"] = description

        # Generate images using image generator
        images = self.image_generator.generate_product_images(
            product_name, product_id, product_for_content
        )

        # Create final product
        product = {
            "id": product_id,
            "name": product_name,
            "description": description,
            "category": category,
            "brand": brand,
            "price": price,
            "currency": "USD",
            "in_stock": random.choice([True, True, True, False]),  # 75% in stock
            "stock_quantity": random.randint(1, 100) if random.random() < 0.9 else 1,
            "rating": round(random.uniform(3.0, 5.0), 1),
            "review_count": random.randint(0, 500),
            "sku": f"{category[:3].upper()}-{product_id:06d}",
            "weight": round(random.uniform(0.1, 5.0), 2),
            "dimensions": {
                "length": round(random.uniform(5, 50), 1),
                "width": round(random.uniform(5, 50), 1),
                "height": round(random.uniform(2, 30), 1),
                "unit": "cm",
            },
            "features": features,
            "images": images,
            "tags": self.generate_product_tags(category, product_type, features),
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
            "updated_at": self.fake.date_time_between(
                start_date="-30d", end_date="now"
            ),
        }

        return product

    def generate_product_tags(
        self, category: str, product_type: str, features: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant tags for the product."""
        tags = [category.lower(), product_type.lower()]

        # Add feature-based tags
        if "color" in features:
            tags.append(features["color"].lower())
        if "material" in features:
            tags.append(features["material"].lower())
        if "size" in features:
            tags.append(f"size-{features['size'].lower()}")

        # Add category-specific tags
        if category == "Electronics":
            tags.extend(["tech", "gadget", "device"])
            if any(x in product_type.lower() for x in ["phone", "smartphone"]):
                tags.extend(["mobile", "communication"])
            elif any(x in product_type.lower() for x in ["laptop", "computer"]):
                tags.extend(["computing", "work"])
        elif category == "Clothing":
            tags.extend(["fashion", "apparel", "style"])
        elif category == "Books":
            tags.extend(["reading", "education", "literature"])
        elif category == "Home & Garden":
            tags.extend(["home", "household", "domestic"])
        elif category == "Sports":
            tags.extend(["fitness", "exercise", "athletic"])

        return list(set(tags))  # Remove duplicates

    def generate_products(self, count: int, starting_id: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple products."""
        products = []

        # Distribute products across categories
        categories = list(PRODUCT_CATEGORIES.keys())
        products_per_category = count // len(categories)
        remaining = count % len(categories)

        product_id = starting_id

        for i, category in enumerate(categories):
            category_count = products_per_category
            if i < remaining:
                category_count += 1

            for _ in range(category_count):
                product = self.generate_product(product_id, category)
                products.append(product)
                product_id += 1

                if product_id % 50 == 0:
                    print(f"Generated {product_id - 1} products...")

        return products
