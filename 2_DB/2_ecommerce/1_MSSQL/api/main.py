"""
MSSQL FastAPI service for e-commerce core business data.
Handles products, users, orders, and transactions with ACID compliance.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import uvicorn
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
import json
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-commerce MSSQL API",
    description="Core business data API using Microsoft SQL Server",
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

# Database connection
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost,1433;"
    "DATABASE=ECommerceDB;"
    "UID=sa;"
    "PWD=Heslo_1234;"
    "TrustServerCertificate=yes;"
    "Encrypt=no;"
)


def get_engine():
    sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={CONNECTION_STRING}"
    return create_engine(sqlalchemy_url, poolclass=NullPool)


def get_db():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            yield conn
    finally:
        engine.dispose()


# Pydantic models
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    price: float
    stock_quantity: int
    brand: Optional[str]
    sku: Optional[str]
    rating: Optional[float]
    review_count: int
    is_active: bool
    main_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedProductsResponse(BaseModel):
    products: List[ProductResponse]
    pagination: PaginationInfo


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    total_orders: int
    total_spent: float
    is_active: bool
    join_date: datetime

class UserListItem(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    is_premium: bool
    total_orders: int
    total_spent: float
    average_order_value: float
    created_at: str
    updated_at: str

class UsersListResponse(BaseModel):
    users: List[UserListItem]
    total: int


class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_date: datetime
    status: str
    total_amount: float
    item_count: int


class OrderDetailResponse(BaseModel):
    id: int
    user_id: int
    order_date: datetime
    status: str
    subtotal: float
    shipping_cost: float
    tax_amount: float
    total_amount: float
    payment_method: str
    shipping_address: str
    items: List[Dict[str, Any]]


class OrderCreate(BaseModel):
    user_id: int
    items: List[Dict[str, Any]]  # [{"product_id": int, "quantity": int}]
    shipping_address: Dict[str, str]
    payment_method: str


class SalesReport(BaseModel):
    total_revenue: float
    total_orders: int
    avg_order_value: float
    top_categories: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]


# API Routes


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.get("/products", response_model=PaginatedProductsResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: bool = True,
    db=Depends(get_db),
):
    """Get products with filtering and pagination."""
    try:
        # Build base query for filtering
        base_where = "WHERE p.IsActive = 1"
        params = {}

        if category:
            base_where += " AND c.Name = :category"
            params["category"] = category

        if min_price is not None:
            base_where += " AND p.Price >= :min_price"
            params["min_price"] = min_price

        if max_price is not None:
            base_where += " AND p.Price <= :max_price"
            params["max_price"] = max_price

        if in_stock:
            base_where += " AND p.StockQuantity > 0"

        # Count total items
        count_query = f"""
            SELECT COUNT(*)
            FROM Products p
            LEFT JOIN Categories c ON p.CategoryId = c.Id
            {base_where}
        """
        
        count_result = db.execute(text(count_query), params)
        total_items = count_result.scalar()

        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1

        # Get products with pagination
        products_query = f"""
            SELECT p.Id, p.Name, p.Description, c.Name as Category, 
                   p.Price, p.StockQuantity, p.Brand, p.SKU, 
                   p.Rating, p.ReviewCount, p.IsActive,
                   p.MainImageUrl, p.ThumbnailUrl
            FROM Products p
            LEFT JOIN Categories c ON p.CategoryId = c.Id
            {base_where}
            ORDER BY p.Id OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
        """
        params["skip"] = skip
        params["limit"] = page_size

        result = db.execute(text(products_query), params)
        products = []

        for row in result:
            products.append(
                ProductResponse(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    category=row[3],
                    price=float(row[4]),
                    stock_quantity=row[5],
                    brand=row[6],
                    sku=row[7],
                    rating=float(row[8]) if row[8] else None,
                    review_count=row[9],
                    is_active=row[10],
                    main_image_url=row[11],
                    thumbnail_url=row[12],
                )
            )

        # Create pagination info
        pagination_info = PaginationInfo(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )

        return PaginatedProductsResponse(
            products=products,
            pagination=pagination_info
        )

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db=Depends(get_db)):
    """Get a specific product by ID."""
    try:
        query = """
            SELECT p.Id, p.Name, p.Description, c.Name as Category,
                   p.Price, p.StockQuantity, p.Brand, p.SKU,
                   p.Rating, p.ReviewCount, p.IsActive,
                   p.MainImageUrl, p.ThumbnailUrl
            FROM Products p
            LEFT JOIN Categories c ON p.CategoryId = c.Id
            WHERE p.Id = :product_id AND p.IsActive = 1
        """

        result = db.execute(text(query), {"product_id": product_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductResponse(
            id=row[0],
            name=row[1],
            description=row[2],
            category=row[3],
            price=float(row[4]),
            stock_quantity=row[5],
            brand=row[6],
            sku=row[7],
            rating=float(row[8]) if row[8] else None,
            review_count=row[9],
            is_active=row[10],
            main_image_url=row[11],
            thumbnail_url=row[12],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch product")


@app.get("/users", response_model=UsersListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of users per page")
):
    """Get paginated list of users from shared data."""
    try:
        # Load users from shared data file
        shared_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared_data", "users.json")
        
        with open(shared_data_path, 'r') as f:
            all_users_data = json.load(f)
        
        # Calculate pagination
        total_users = len(all_users_data)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_users = all_users_data[start_idx:end_idx]
        
        # Convert to response format with calculated totals
        users = []
        for user_data in page_users:
            # Calculate total orders from database
            try:
                orders_query = """
                    SELECT COUNT(*) as total_orders, ISNULL(SUM(TotalAmount), 0) as total_spent
                    FROM Orders 
                    WHERE UserId = :user_id
                """
                result = None
                try:
                    engine = get_engine()
                    with engine.connect() as conn:
                        result = conn.execute(text(orders_query), {"user_id": user_data["id"]})
                        row = result.fetchone()
                        actual_total_orders = row[0] if row else 0
                        actual_total_spent = float(row[1]) if row else 0.0
                        actual_avg_order_value = actual_total_spent / actual_total_orders if actual_total_orders > 0 else 0.0
                    engine.dispose()
                except Exception as db_error:
                    logger.warning(f"Failed to get orders for user {user_data['id']}: {db_error}")
                    actual_total_orders = 0
                    actual_total_spent = 0.0
                    actual_avg_order_value = 0.0
                
                users.append(UserListItem(
                    id=user_data["id"],
                    email=user_data["email"],
                    username=user_data["username"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    is_active=user_data["is_active"],
                    is_premium=user_data["is_premium"],
                    total_orders=actual_total_orders,
                    total_spent=actual_total_spent,
                    average_order_value=actual_avg_order_value,
                    created_at=user_data["registration_date"],
                    updated_at=user_data.get("last_login", user_data["registration_date"])
                ))
            except Exception as user_error:
                logger.error(f"Error processing user {user_data.get('id', 'unknown')}: {user_error}")
                continue
        
        return UsersListResponse(
            users=users,
            total=total_users
        )
        
    except FileNotFoundError:
        logger.error(f"Users data file not found at {shared_data_path}")
        raise HTTPException(status_code=500, detail="Users data not available")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse users data: {e}")
        raise HTTPException(status_code=500, detail="Invalid users data format")
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db=Depends(get_db)):
    """Get user information."""
    try:
        query = """
            SELECT Id, Email, FirstName, LastName, TotalOrders, 
                   TotalSpent, IsActive, JoinDate
            FROM Users
            WHERE Id = :user_id
        """

        result = db.execute(text(query), {"user_id": user_id})
        row = result.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=row[0],
            email=row[1],
            first_name=row[2],
            last_name=row[3],
            total_orders=row[4],
            total_spent=float(row[5]),
            is_active=row[6],
            join_date=row[7],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")


@app.get("/users/{user_id}/orders", response_model=List[OrderDetailResponse])
async def get_user_orders(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db=Depends(get_db),
):
    """Get user's order history with full item details."""
    try:
        # First check if user exists
        user_check = db.execute(
            text("SELECT 1 FROM Users WHERE Id = :user_id"), {"user_id": user_id}
        )
        if not user_check.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Get orders with details
        orders_query = """
            SELECT o.Id, o.UserId, o.OrderDate, o.Status, 
                   ISNULL(o.Subtotal, 0) as Subtotal,
                   ISNULL(o.ShippingCost, 0) as ShippingCost,
                   ISNULL(o.TaxAmount, 0) as TaxAmount,
                   o.TotalAmount,
                   ISNULL(o.PaymentMethod, 'Credit Card') as PaymentMethod,
                   ISNULL(CONCAT(o.ShippingStreet, ', ', o.ShippingCity, ', ', o.ShippingState), 'Standard Shipping') as ShippingAddress
            FROM Orders o
            WHERE o.UserId = :user_id
            ORDER BY o.OrderDate DESC
            OFFSET :skip ROWS FETCH NEXT :limit ROWS ONLY
        """

        orders_result = db.execute(
            text(orders_query), {"user_id": user_id, "skip": skip, "limit": limit}
        )
        
        # Fetch all order rows first to avoid connection busy error
        order_rows = orders_result.fetchall()
        orders = []

        for order_row in order_rows:
            order_id = order_row[0]
            
            # Get order items for this order
            items_query = """
                SELECT ProductId, ProductName, Quantity, UnitPrice, TotalPrice
                FROM OrderItems
                WHERE OrderId = :order_id
            """

            items_result = db.execute(text(items_query), {"order_id": order_id})
            items = []

            for item_row in items_result.fetchall():
                items.append(
                    {
                        "product_id": item_row[0],
                        "product_name": item_row[1],
                        "quantity": item_row[2],
                        "unit_price": float(item_row[3]),
                        "total_price": float(item_row[4]),
                    }
                )

            orders.append(
                OrderDetailResponse(
                    id=order_row[0],
                    user_id=order_row[1],
                    order_date=order_row[2],
                    status=order_row[3],
                    subtotal=float(order_row[4]),
                    shipping_cost=float(order_row[5]),
                    tax_amount=float(order_row[6]),
                    total_amount=float(order_row[7]),
                    payment_method=order_row[8],
                    shipping_address=order_row[9],
                    items=items,
                )
            )

        return orders

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching orders for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user orders")


@app.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order_detail(order_id: int, db=Depends(get_db)):
    """Get detailed order information."""
    try:
        # Get order details
        order_query = """
            SELECT Id, UserId, OrderDate, Status, Subtotal, 
                   ShippingCost, TaxAmount, TotalAmount
            FROM Orders
            WHERE Id = :order_id
        """

        order_result = db.execute(text(order_query), {"order_id": order_id})
        order_row = order_result.fetchone()

        if not order_row:
            raise HTTPException(status_code=404, detail="Order not found")

        # Get order items
        items_query = """
            SELECT ProductId, ProductName, Quantity, UnitPrice, TotalPrice
            FROM OrderItems
            WHERE OrderId = :order_id
        """

        items_result = db.execute(text(items_query), {"order_id": order_id})
        items = []

        for item_row in items_result:
            items.append(
                {
                    "product_id": item_row[0],
                    "product_name": item_row[1],
                    "quantity": item_row[2],
                    "unit_price": float(item_row[3]),
                    "total_price": float(item_row[4]),
                }
            )

        return OrderDetailResponse(
            id=order_row[0],
            user_id=order_row[1],
            order_date=order_row[2],
            status=order_row[3],
            subtotal=float(order_row[4]),
            shipping_cost=float(order_row[5]),
            tax_amount=float(order_row[6]),
            total_amount=float(order_row[7]),
            items=items,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch order details")


@app.post("/orders", response_model=OrderDetailResponse)
async def create_order(order: OrderCreate, db=Depends(get_db)):
    """Create a new order with ACID transaction."""
    try:
        # Start transaction
        trans = db.begin()

        try:
            # Verify user exists
            user_check = db.execute(
                text("SELECT 1 FROM Users WHERE Id = :user_id"),
                {"user_id": order.user_id},
            )
            if not user_check.fetchone():
                raise HTTPException(status_code=404, detail="User not found")

            # Calculate order totals
            subtotal = 0.0
            order_items = []

            for item in order.items:
                # Get product info and check stock
                product_query = """
                    SELECT Id, Name, Price, StockQuantity 
                    FROM Products 
                    WHERE Id = :product_id AND IsActive = 1
                """
                product_result = db.execute(
                    text(product_query), {"product_id": item["product_id"]}
                )
                product_row = product_result.fetchone()

                if not product_row:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product {item['product_id']} not found",
                    )

                if product_row[3] < item["quantity"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {item['product_id']}",
                    )

                item_total = float(product_row[2]) * item["quantity"]
                subtotal += item_total

                order_items.append(
                    {
                        "product_id": product_row[0],
                        "product_name": product_row[1],
                        "quantity": item["quantity"],
                        "unit_price": float(product_row[2]),
                        "total_price": item_total,
                    }
                )

            # Calculate tax and shipping
            shipping_cost = 0.0 if subtotal > 50 else 9.99
            tax_amount = subtotal * 0.08  # 8% tax
            total_amount = subtotal + shipping_cost + tax_amount

            # Get next order ID
            next_id_result = db.execute(
                text("SELECT ISNULL(MAX(Id), 0) + 1 FROM Orders")
            )
            next_order_id = next_id_result.scalar()

            # Insert order
            insert_order_query = """
                INSERT INTO Orders (
                    Id, UserId, OrderDate, Status, Subtotal, ShippingCost, 
                    TaxAmount, TotalAmount, ShippingStreet, ShippingCity, 
                    ShippingState, ShippingZipCode, ShippingCountry, PaymentMethod
                ) VALUES (
                    :order_id, :user_id, GETDATE(), 'pending', :subtotal, :shipping_cost,
                    :tax_amount, :total_amount, :street, :city, 
                    :state, :zip_code, :country, :payment_method
                )
            """

            db.execute(
                text(insert_order_query),
                {
                    "order_id": next_order_id,
                    "user_id": order.user_id,
                    "subtotal": subtotal,
                    "shipping_cost": shipping_cost,
                    "tax_amount": tax_amount,
                    "total_amount": total_amount,
                    "street": order.shipping_address.get("street", ""),
                    "city": order.shipping_address.get("city", ""),
                    "state": order.shipping_address.get("state", ""),
                    "zip_code": order.shipping_address.get("zip_code", ""),
                    "country": order.shipping_address.get("country", ""),
                    "payment_method": order.payment_method,
                },
            )

            # Insert order items and update inventory
            for item in order_items:
                # Insert order item
                insert_item_query = """
                    INSERT INTO OrderItems (OrderId, ProductId, ProductName, Quantity, UnitPrice, TotalPrice)
                    VALUES (:order_id, :product_id, :product_name, :quantity, :unit_price, :total_price)
                """

                db.execute(
                    text(insert_item_query),
                    {
                        "order_id": next_order_id,
                        "product_id": item["product_id"],
                        "product_name": item["product_name"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "total_price": item["total_price"],
                    },
                )

                # Update inventory
                update_inventory_query = """
                    UPDATE Products 
                    SET StockQuantity = StockQuantity - :quantity 
                    WHERE Id = :product_id
                """

                db.execute(
                    text(update_inventory_query),
                    {"quantity": item["quantity"], "product_id": item["product_id"]},
                )

            # Insert payment record
            insert_payment_query = """
                INSERT INTO Payments (OrderId, PaymentMethod, Amount, Status, TransactionId)
                VALUES (:order_id, :payment_method, :amount, 'pending', :transaction_id)
            """

            db.execute(
                text(insert_payment_query),
                {
                    "order_id": next_order_id,
                    "payment_method": order.payment_method,
                    "amount": total_amount,
                    "transaction_id": f"TXN-{next_order_id:06d}",
                },
            )

            # Update user statistics
            update_user_query = """
                UPDATE Users 
                SET TotalOrders = TotalOrders + 1, TotalSpent = TotalSpent + :amount
                WHERE Id = :user_id
            """

            db.execute(
                text(update_user_query),
                {"amount": total_amount, "user_id": order.user_id},
            )

            # Commit transaction
            trans.commit()

            # Return created order
            return OrderDetailResponse(
                id=next_order_id,
                user_id=order.user_id,
                order_date=datetime.now(),
                status="pending",
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total_amount=total_amount,
                items=order_items,
            )

        except Exception as e:
            trans.rollback()
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")


@app.get("/reports/sales", response_model=SalesReport)
async def get_sales_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db=Depends(get_db),
):
    """Generate sales analytics report."""
    try:
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()

        # Total revenue and orders
        summary_query = """
            SELECT 
                COUNT(*) as TotalOrders,
                ISNULL(SUM(TotalAmount), 0) as TotalRevenue,
                ISNULL(AVG(TotalAmount), 0) as AvgOrderValue
            FROM Orders
            WHERE OrderDate >= :start_date AND OrderDate <= :end_date
            AND Status IN ('shipped', 'delivered')
        """

        summary_result = db.execute(
            text(summary_query), {"start_date": start_date, "end_date": end_date}
        )
        summary_row = summary_result.fetchone()

        # Top categories
        category_query = """
            SELECT TOP 5 c.Name, 
                   SUM(oi.TotalPrice) as Revenue,
                   COUNT(DISTINCT o.Id) as Orders
            FROM Orders o
            JOIN OrderItems oi ON o.Id = oi.OrderId
            JOIN Products p ON oi.ProductId = p.Id
            JOIN Categories c ON p.CategoryId = c.Id
            WHERE o.OrderDate >= :start_date AND o.OrderDate <= :end_date
            AND o.Status IN ('shipped', 'delivered')
            GROUP BY c.Name
            ORDER BY Revenue DESC
        """

        category_result = db.execute(
            text(category_query), {"start_date": start_date, "end_date": end_date}
        )

        top_categories = []
        for row in category_result:
            top_categories.append(
                {"category": row[0], "revenue": float(row[1]), "orders": row[2]}
            )

        # Top products
        product_query = """
            SELECT TOP 5 p.Name, 
                   SUM(oi.Quantity) as QuantitySold,
                   SUM(oi.TotalPrice) as Revenue
            FROM Orders o
            JOIN OrderItems oi ON o.Id = oi.OrderId
            JOIN Products p ON oi.ProductId = p.Id
            WHERE o.OrderDate >= :start_date AND o.OrderDate <= :end_date
            AND o.Status IN ('shipped', 'delivered')
            GROUP BY p.Name
            ORDER BY Revenue DESC
        """

        product_result = db.execute(
            text(product_query), {"start_date": start_date, "end_date": end_date}
        )

        top_products = []
        for row in product_result:
            top_products.append(
                {"product": row[0], "quantity_sold": row[1], "revenue": float(row[2])}
            )

        return SalesReport(
            total_revenue=float(summary_row[1]),
            total_orders=summary_row[0],
            avg_order_value=float(summary_row[2]),
            top_categories=top_categories,
            top_products=top_products,
        )

    except Exception as e:
        logger.error(f"Error generating sales report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate sales report")


@app.get("/categories")
async def get_categories(db=Depends(get_db)):
    """Get all product categories."""
    try:
        query = "SELECT Id, Name, Description FROM Categories ORDER BY Name"
        result = db.execute(text(query))

        categories = []
        for row in result:
            categories.append({"id": row[0], "name": row[1], "description": row[2]})

        return categories

    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
