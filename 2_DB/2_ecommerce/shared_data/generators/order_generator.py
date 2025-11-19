"""
Order generation functionality.
Handles order creation with realistic order patterns and relationships.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from faker import Faker

from .base_generator import BaseGenerator


class OrderGenerator(BaseGenerator):
    """Handles order generation with realistic data."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_order_status_history(self, order_date: datetime) -> List[Dict[str, Any]]:
        """Generate realistic order status progression."""
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered"]
        
        # Some orders might be cancelled or returned
        if random.random() < 0.05:  # 5% chance of cancellation
            statuses = ["pending", "cancelled"]
        elif random.random() < 0.03:  # 3% chance of return after delivery
            statuses.extend(["returned"])
        
        history = []
        current_date = order_date
        
        for i, status in enumerate(statuses):
            if status == "cancelled":
                # Cancellation can happen at any early stage
                break
            
            # Add realistic time delays between statuses
            if i > 0:
                if status == "confirmed":
                    current_date += timedelta(hours=random.randint(1, 24))
                elif status == "processing":
                    current_date += timedelta(hours=random.randint(2, 48))
                elif status == "shipped":
                    current_date += timedelta(days=random.randint(1, 3))
                elif status == "delivered":
                    current_date += timedelta(days=random.randint(2, 7))
                elif status == "returned":
                    current_date += timedelta(days=random.randint(5, 30))
            
            history.append({
                "status": status,
                "timestamp": current_date,
                "note": self.generate_status_note(status)
            })
        
        return history

    def generate_status_note(self, status: str) -> str:
        """Generate status-appropriate notes."""
        notes = {
            "pending": ["Order received", "Payment pending", "Awaiting confirmation"],
            "confirmed": ["Payment confirmed", "Order confirmed", "Processing started"],
            "processing": ["Preparing items", "Items collected", "Packaging in progress"],
            "shipped": ["Order shipped", "Package in transit", "Tracking number assigned"],
            "delivered": ["Package delivered", "Delivery confirmed", "Order completed"],
            "cancelled": ["Order cancelled by customer", "Payment failed", "Item out of stock"],
            "returned": ["Return requested", "Item returned", "Refund processed"]
        }
        return random.choice(notes.get(status, ["Status updated"]))

    def generate_shipping_info(self) -> Dict[str, Any]:
        """Generate shipping information."""
        carriers = ["FedEx", "UPS", "DHL", "USPS", "Amazon Logistics"]
        services = ["Standard", "Express", "Next Day", "2-Day", "Ground"]
        
        carrier = random.choice(carriers)
        service = random.choice(services)
        
        return {
            "carrier": carrier,
            "service": service,
            "tracking_number": f"{carrier[:3].upper()}{random.randint(100000000, 999999999)}",
            "estimated_delivery": self.fake.date_between(start_date="today", end_date="+10d"),
            "shipping_cost": round(random.uniform(5.99, 29.99), 2),
        }

    def generate_payment_info(self, total_amount: float) -> Dict[str, Any]:
        """Generate payment information."""
        payment_methods = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]
        
        payment_method = random.choice(payment_methods)
        
        payment_info = {
            "method": payment_method,
            "amount": total_amount,
            "currency": "USD",
            "status": random.choice(["completed", "completed", "completed", "failed"]),  # 75% success
            "transaction_id": f"TXN{random.randint(1000000000, 9999999999)}",
            "processed_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
        }
        
        if payment_method == "credit_card":
            payment_info.update({
                "card_type": random.choice(["Visa", "Mastercard", "American Express"]),
                "last_four": f"{random.randint(1000, 9999)}",
            })
        elif payment_method == "paypal":
            payment_info.update({
                "paypal_transaction_id": f"PAY{random.randint(100000000, 999999999)}"
            })
        
        return payment_info

    def generate_order_items(self, products: List[Dict[str, Any]], max_items: int = 5) -> List[Dict[str, Any]]:
        """Generate order items from available products."""
        num_items = random.randint(1, min(max_items, len(products)))
        selected_products = random.sample(products, num_items)
        
        order_items = []
        for product in selected_products:
            quantity = random.randint(1, 3)
            item_price = product["price"]
            
            # Apply random discount occasionally
            discount = 0
            if random.random() < 0.15:  # 15% chance of discount
                discount = round(random.uniform(0.05, 0.3), 2)  # 5-30% discount
                item_price = round(item_price * (1 - discount), 2)
            
            order_items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"],
                "discounted_price": item_price,
                "discount_percentage": discount,
                "total_price": round(item_price * quantity, 2),
                "sku": product["sku"],
                "category": product["category"],
            })
        
        return order_items

    def calculate_order_totals(self, order_items: List[Dict[str, Any]], shipping_cost: float = 0) -> Dict[str, float]:
        """Calculate order totals."""
        subtotal = sum(item["total_price"] for item in order_items)
        tax_rate = 0.08  # 8% tax
        tax_amount = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax_amount + shipping_cost, 2)
        
        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "total": total,
        }

    def generate_order(
        self, 
        order_id: int, 
        user: Dict[str, Any], 
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a single order with all attributes."""
        
        # Generate order date (more recent orders are more likely)
        order_date = self.fake.date_time_between(start_date="-1y", end_date="now")
        
        # Generate order items
        order_items = self.generate_order_items(products)
        
        # Generate shipping info
        shipping_info = self.generate_shipping_info()
        
        # Calculate totals
        totals = self.calculate_order_totals(order_items, shipping_info["shipping_cost"])
        
        # Generate payment info
        payment_info = self.generate_payment_info(totals["total"])
        
        # Generate status history
        status_history = self.generate_order_status_history(order_date)
        current_status = status_history[-1]["status"]
        
        order = {
            "id": order_id,
            "order_number": f"ORD{order_id:08d}",
            "user_id": user["id"],
            "user_email": user["email"],
            "order_date": order_date,
            "status": current_status,
            "items": order_items,
            "totals": totals,
            "shipping_address": user["shipping_address"].copy(),
            "billing_address": user["billing_address"].copy(),
            "shipping_info": shipping_info,
            "payment_info": payment_info,
            "status_history": status_history,
            "notes": self.generate_order_notes(),
            "created_at": order_date,
            "updated_at": status_history[-1]["timestamp"],
        }
        
        return order

    def generate_order_notes(self) -> List[str]:
        """Generate order notes."""
        possible_notes = [
            "Customer requested expedited shipping",
            "Gift wrapping requested",
            "Delivery to front door",
            "Call before delivery",
            "Leave with neighbor if not home",
            "Business address - deliver during office hours",
            "Fragile items - handle with care",
        ]
        
        if random.random() < 0.3:  # 30% chance of having notes
            return random.sample(possible_notes, random.randint(1, 2))
        return []

    def generate_orders(
        self, 
        users: List[Dict[str, Any]], 
        products: List[Dict[str, Any]], 
        orders_per_user_range: tuple = (0, 10),
        starting_id: int = 1
    ) -> List[Dict[str, Any]]:
        """Generate orders for users."""
        orders = []
        order_id = starting_id
        
        for user in users:
            # Generate random number of orders for this user
            num_orders = random.randint(*orders_per_user_range)
            
            # Some users have no orders
            if user["stats"]["orders_count"] == 0:
                num_orders = 0
            else:
                # Respect the user's order count if it's reasonable
                if user["stats"]["orders_count"] <= 20:
                    num_orders = min(num_orders, user["stats"]["orders_count"])
            
            for _ in range(num_orders):
                order = self.generate_order(order_id, user, products)
                orders.append(order)
                order_id += 1
            
            if order_id % 100 == 0:
                print(f"Generated {order_id - 1} orders...")
        
        return orders