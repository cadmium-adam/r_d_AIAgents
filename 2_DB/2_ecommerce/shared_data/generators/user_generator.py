"""
User generation functionality.
Handles user account creation with realistic profiles and preferences.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from faker import Faker

from .base_generator import BaseGenerator


class UserGenerator(BaseGenerator):
    """Handles user generation with realistic data."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_user_preferences(self) -> Dict[str, Any]:
        """Generate user preferences and settings."""
        return {
            "newsletter": random.choice([True, False]),
            "marketing_emails": random.choice([True, False]),
            "preferred_categories": random.sample([
                "Electronics", "Clothing", "Books", "Home & Garden", "Sports"
            ], k=random.randint(1, 3)),
            "language": random.choice(["en", "es", "fr", "de"]),
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "notifications": {
                "order_updates": random.choice([True, False]),
                "price_drops": random.choice([True, False]),
                "new_arrivals": random.choice([True, False]),
            }
        }

    def generate_shipping_address(self) -> Dict[str, Any]:
        """Generate realistic shipping address."""
        return {
            "street": self.fake.street_address(),
            "city": self.fake.city(),
            "state": self.fake.state(),
            "postal_code": self.fake.postcode(),
            "country": self.fake.country_code(),
            "is_default": True,
        }

    def generate_billing_address(self, shipping_address: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate billing address (sometimes same as shipping)."""
        if shipping_address and random.random() < 0.7:  # 70% chance same as shipping
            billing = shipping_address.copy()
            billing["is_default"] = True
            return billing
        else:
            return {
                "street": self.fake.street_address(),
                "city": self.fake.city(),
                "state": self.fake.state(),
                "postal_code": self.fake.postcode(),
                "country": self.fake.country_code(),
                "is_default": True,
            }

    def generate_user_stats(self) -> Dict[str, Any]:
        """Generate user activity statistics."""
        orders_count = random.randint(0, 50)
        total_spent = round(random.uniform(0, 5000), 2) if orders_count > 0 else 0
        
        return {
            "orders_count": orders_count,
            "total_spent": total_spent,
            "average_order_value": round(total_spent / orders_count, 2) if orders_count > 0 else 0,
            "last_login": self.fake.date_time_between(start_date="-30d", end_date="now"),
            "login_count": random.randint(orders_count, orders_count * 5 + 10),
            "wishlist_items": random.randint(0, 20),
            "cart_items": random.randint(0, 5),
        }

    def generate_user(self, user_id: int) -> Dict[str, Any]:
        """Generate a single user with all attributes."""
        # Basic user info
        gender = random.choice(['male', 'female'])
        first_name = self.fake.first_name_male() if gender == 'male' else self.fake.first_name_female()
        last_name = self.fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{self.fake.free_email_domain()}"
        
        # Membership info
        is_premium = random.choice([True, False])
        registration_date = self.fake.date_time_between(start_date="-2y", end_date="now")
        
        # Generate addresses
        shipping_address = self.generate_shipping_address()
        billing_address = self.generate_billing_address(shipping_address)
        
        # Generate user stats
        stats = self.generate_user_stats()
        
        # Generate preferences
        preferences = self.generate_user_preferences()
        
        user = {
            "id": user_id,
            "email": email,
            "username": f"{first_name.lower()}{random.randint(100, 9999)}",
            "first_name": first_name,
            "last_name": last_name,
            "phone": self.fake.phone_number(),
            "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=80),
            "gender": gender,
            "is_active": random.choice([True, True, True, False]),  # 75% active
            "is_premium": is_premium,
            "email_verified": random.choice([True, True, False]),  # 67% verified
            "registration_date": registration_date,
            "last_login": stats["last_login"],
            "shipping_address": shipping_address,
            "billing_address": billing_address,
            "preferences": preferences,
            "stats": stats,
            "loyalty_points": random.randint(0, 10000) if is_premium else random.randint(0, 1000),
            "referral_code": f"REF{user_id:06d}",
            "created_at": registration_date,
            "updated_at": self.fake.date_time_between(start_date=registration_date, end_date="now"),
        }
        
        return user

    def generate_users(self, count: int, starting_id: int = 1) -> List[Dict[str, Any]]:
        """Generate multiple users."""
        users = []
        
        for i in range(count):
            user_id = starting_id + i
            user = self.generate_user(user_id)
            users.append(user)
            
            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1} users...")
        
        return users