"""
MSSQL database population script for e-commerce data.
Handles core business data: products, users, orders, and payments.

Usage:
    python populate_data.py [--recreate|--append]

Modes:
    --recreate (default): Drop and recreate database, overwriting all data
    --append: Add new data to existing database, preserving existing records
"""

import json
import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Add shared_data to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


class MSSQLPopulator:
    """Populates MSSQL database with e-commerce data."""

    def __init__(self, append_mode: bool = False):
        self.connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=master;"
            "UID=sa;"
            "PWD=Heslo_1234;"
            "TrustServerCertificate=yes;"
            "Encrypt=no;"
        )
        self.db_name = "ECommerceDB"
        self.append_mode = append_mode

    def get_engine(self, database: str = None):
        """Create SQLAlchemy engine."""
        conn_str = self.connection_string
        if database:
            conn_str = conn_str.replace("DATABASE=master", f"DATABASE={database}")

        # Convert pyodbc connection string to SQLAlchemy format
        sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={conn_str}"
        return create_engine(sqlalchemy_url, poolclass=NullPool)

    def create_database(self):
        """Create the e-commerce database and tables."""
        if self.append_mode:
            print("Append mode: Ensuring database and tables exist...")
            self._ensure_database_exists()
        else:
            print("Recreate mode: Creating fresh database and tables...")
            self._recreate_database()

    def _recreate_database(self):
        """Drop and recreate the database (original behavior)."""
        # Use raw pyodbc connection for database creation to avoid transaction issues
        conn = pyodbc.connect(self.connection_string, autocommit=True)
        cursor = conn.cursor()

        try:
            # Drop database if it exists, then create it fresh
            cursor.execute(
                f"""
                IF EXISTS (SELECT name FROM sys.databases WHERE name = '{self.db_name}')
                BEGIN
                    ALTER DATABASE [{self.db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    DROP DATABASE [{self.db_name}];
                END
                CREATE DATABASE [{self.db_name}];
            """
            )
        finally:
            cursor.close()
            conn.close()

        # Now connect to the new database and create tables
        self._create_tables()

    def _ensure_database_exists(self):
        """Create database only if it doesn't exist (append mode)."""
        conn = pyodbc.connect(self.connection_string, autocommit=True)
        cursor = conn.cursor()

        try:
            # Create database only if it doesn't exist
            cursor.execute(
                f"""
                IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{self.db_name}')
                BEGIN
                    CREATE DATABASE [{self.db_name}];
                END
            """
            )
        finally:
            cursor.close()
            conn.close()

        # Now connect to the new database and create tables
        self._create_tables()

    def _create_tables(self):
        """Create all tables in the database."""
        engine = self.get_engine(self.db_name)

        with engine.connect() as conn:
            # Create Users table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
                CREATE TABLE Users (
                    Id INT PRIMARY KEY,
                    Email NVARCHAR(255) UNIQUE NOT NULL,
                    FirstName NVARCHAR(100) NOT NULL,
                    LastName NVARCHAR(100) NOT NULL,
                    Phone NVARCHAR(50),
                    DateOfBirth DATE,
                    Street NVARCHAR(255),
                    City NVARCHAR(100),
                    State NVARCHAR(100),
                    ZipCode NVARCHAR(20),
                    Country NVARCHAR(100),
                    IsActive BIT DEFAULT 1,
                    JoinDate DATETIME2 DEFAULT GETDATE(),
                    LastLogin DATETIME2,
                    TotalOrders INT DEFAULT 0,
                    TotalSpent DECIMAL(10,2) DEFAULT 0.00,
                    NewsletterOptIn BIT DEFAULT 0,
                    SMSNotifications BIT DEFAULT 0,
                    CreatedAt DATETIME2 DEFAULT GETDATE(),
                    UpdatedAt DATETIME2 DEFAULT GETDATE()
                )
            """
                )
            )

            # Create Categories table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Categories' AND xtype='U')
                CREATE TABLE Categories (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    Name NVARCHAR(100) UNIQUE NOT NULL,
                    Description NVARCHAR(500),
                    CreatedAt DATETIME2 DEFAULT GETDATE()
                )
            """
                )
            )

            # Create Products table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Products' AND xtype='U')
                CREATE TABLE Products (
                    Id INT PRIMARY KEY,
                    Name NVARCHAR(255) NOT NULL,
                    Description NTEXT,
                    CategoryId INT,
                    Price DECIMAL(10,2) NOT NULL,
                    StockQuantity INT DEFAULT 0,
                    Brand NVARCHAR(100),
                    SKU NVARCHAR(50) UNIQUE,
                    Weight DECIMAL(8,2),
                    Length DECIMAL(8,1),
                    Width DECIMAL(8,1),
                    Height DECIMAL(8,1),
                    Rating DECIMAL(3,1),
                    ReviewCount INT DEFAULT 0,
                    MainImageUrl NVARCHAR(500),
                    ThumbnailUrl NVARCHAR(500),
                    Features NVARCHAR(MAX),
                    IsActive BIT DEFAULT 1,
                    CreatedAt DATETIME2 DEFAULT GETDATE(),
                    UpdatedAt DATETIME2 DEFAULT GETDATE(),
                    FOREIGN KEY (CategoryId) REFERENCES Categories(Id)
                )
            """
                )
            )

            # Create Orders table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Orders' AND xtype='U')
                CREATE TABLE Orders (
                    Id INT PRIMARY KEY,
                    UserId INT NOT NULL,
                    OrderDate DATETIME2 NOT NULL,
                    Status NVARCHAR(50) NOT NULL,
                    Subtotal DECIMAL(10,2) NOT NULL,
                    ShippingCost DECIMAL(10,2) DEFAULT 0.00,
                    TaxAmount DECIMAL(10,2) DEFAULT 0.00,
                    TotalAmount DECIMAL(10,2) NOT NULL,
                    ShippingStreet NVARCHAR(255),
                    ShippingCity NVARCHAR(100),
                    ShippingState NVARCHAR(100),
                    ShippingZipCode NVARCHAR(20),
                    ShippingCountry NVARCHAR(100),
                    PaymentMethod NVARCHAR(50),
                    TrackingNumber NVARCHAR(50),
                    CreatedAt DATETIME2 DEFAULT GETDATE(),
                    FOREIGN KEY (UserId) REFERENCES Users(Id)
                )
            """
                )
            )

            # Create OrderItems table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='OrderItems' AND xtype='U')
                CREATE TABLE OrderItems (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    OrderId INT NOT NULL,
                    ProductId INT NOT NULL,
                    ProductName NVARCHAR(255) NOT NULL,
                    Quantity INT NOT NULL,
                    UnitPrice DECIMAL(10,2) NOT NULL,
                    TotalPrice DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (OrderId) REFERENCES Orders(Id),
                    FOREIGN KEY (ProductId) REFERENCES Products(Id)
                )
            """
                )
            )

            # Create Payments table
            conn.execute(
                text(
                    """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Payments' AND xtype='U')
                CREATE TABLE Payments (
                    Id INT IDENTITY(1,1) PRIMARY KEY,
                    OrderId INT NOT NULL,
                    PaymentMethod NVARCHAR(50) NOT NULL,
                    Amount DECIMAL(10,2) NOT NULL,
                    Status NVARCHAR(50) NOT NULL,
                    TransactionId NVARCHAR(100),
                    ProcessedAt DATETIME2 DEFAULT GETDATE(),
                    FOREIGN KEY (OrderId) REFERENCES Orders(Id)
                )
            """
                )
            )

            conn.commit()
            print("Database and tables created successfully.")

    def insert_categories(self, products: List[Dict[str, Any]]):
        """Insert unique product categories."""
        print("Inserting categories...")

        # Extract unique categories
        categories = list(set(product["category"] for product in products))

        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            for category in categories:
                conn.execute(
                    text(
                        """
                    IF NOT EXISTS (SELECT 1 FROM Categories WHERE Name = :name)
                    INSERT INTO Categories (Name, Description) 
                    VALUES (:name, :description)
                """
                    ),
                    {
                        "name": category,
                        "description": f"{category} products and accessories",
                    },
                )
            conn.commit()

        print(f"Inserted {len(categories)} categories.")

    def get_category_mapping(self) -> Dict[str, int]:
        """Get mapping of category names to IDs."""
        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT Id, Name FROM Categories"))
            return {row[1]: row[0] for row in result}

    def insert_users(self, users: List[Dict[str, Any]]):
        """Insert users into the database."""
        print(f"Inserting {len(users)} users...")

        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            inserted_count = 0
            skipped_count = 0

            for user in users:
                if self.append_mode:
                    # Check if user already exists
                    existing = conn.execute(
                        text("SELECT Id FROM Users WHERE Id = :id"), {"id": user["id"]}
                    ).fetchone()

                    if existing:
                        skipped_count += 1
                        continue

                conn.execute(
                    text(
                        """
                    INSERT INTO Users (
                        Id, Email, FirstName, LastName, Phone, DateOfBirth,
                        Street, City, State, ZipCode, Country, IsActive,
                        JoinDate, LastLogin, TotalOrders, TotalSpent,
                        NewsletterOptIn, SMSNotifications
                    ) VALUES (
                        :id, :email, :first_name, :last_name, :phone, :date_of_birth,
                        :street, :city, :state, :zip_code, :country, :is_active,
                        :join_date, :last_login, :total_orders, :total_spent,
                        :newsletter, :sms_notifications
                    )
                """
                    ),
                    {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "phone": user["phone"],
                        "date_of_birth": user["date_of_birth"],
                        "street": user["shipping_address"]["street"],
                        "city": user["shipping_address"]["city"],
                        "state": user["shipping_address"]["state"],
                        "zip_code": user["shipping_address"]["postal_code"],
                        "country": user["shipping_address"]["country"],
                        "is_active": user["is_active"],
                        "join_date": user["registration_date"],
                        "last_login": user["last_login"],
                        "total_orders": user["stats"]["orders_count"],
                        "total_spent": user["stats"]["total_spent"],
                        "newsletter": user["preferences"]["newsletter"],
                        "sms_notifications": user["preferences"]["notifications"][
                            "order_updates"
                        ],
                    },
                )
                inserted_count += 1

            conn.commit()

        if self.append_mode:
            print(
                f"Users processed: {inserted_count} inserted, {skipped_count} skipped (already exist)"
            )
        else:
            print(f"Users inserted successfully: {inserted_count}")

    def insert_products(
        self, products: List[Dict[str, Any]], category_mapping: Dict[str, int]
    ):
        """Insert products into the database."""
        print(f"Inserting {len(products)} products...")

        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            inserted_count = 0
            skipped_count = 0

            for product in products:
                if self.append_mode:
                    # Check if product already exists
                    existing = conn.execute(
                        text("SELECT Id FROM Products WHERE Id = :id"),
                        {"id": product["id"]},
                    ).fetchone()

                    if existing:
                        skipped_count += 1
                        continue
                # Prepare image and features data
                main_image = product.get("images", {}).get("main_image", "")
                thumbnail = product.get("images", {}).get("thumbnail", "")
                features_json = (
                    json.dumps(product.get("features", {}))
                    if product.get("features")
                    else ""
                )

                conn.execute(
                    text(
                        """
                    INSERT INTO Products (
                        Id, Name, Description, CategoryId, Price, StockQuantity,
                        Brand, SKU, Weight, Length, Width, Height,
                        Rating, ReviewCount, MainImageUrl, ThumbnailUrl, Features,
                        IsActive, CreatedAt, UpdatedAt
                    ) VALUES (
                        :id, :name, :description, :category_id, :price, :stock_quantity,
                        :brand, :sku, :weight, :length, :width, :height,
                        :rating, :review_count, :main_image, :thumbnail, :features,
                        :is_active, :created_at, :updated_at
                    )
                """
                    ),
                    {
                        "id": product["id"],
                        "name": product["name"],
                        "description": product["description"],
                        "category_id": category_mapping[product["category"]],
                        "price": product["price"],
                        "stock_quantity": product["stock_quantity"],
                        "brand": product["brand"],
                        "sku": product["sku"],
                        "weight": product["weight"],
                        "length": product["dimensions"]["length"],
                        "width": product["dimensions"]["width"],
                        "height": product["dimensions"]["height"],
                        "rating": product["rating"],
                        "review_count": product["review_count"],
                        "main_image": main_image,
                        "thumbnail": thumbnail,
                        "features": features_json,
                        "is_active": product["in_stock"],
                        "created_at": product["created_at"],
                        "updated_at": product["updated_at"],
                    },
                )
                inserted_count += 1

            conn.commit()

        if self.append_mode:
            print(
                f"Products processed: {inserted_count} inserted, {skipped_count} skipped (already exist)"
            )
        else:
            print(f"Products inserted successfully: {inserted_count}")

    def insert_orders_and_items(self, orders: List[Dict[str, Any]]):
        """Insert orders and order items into the database."""
        print(f"Inserting {len(orders)} orders...")

        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            inserted_count = 0
            skipped_count = 0

            for order in orders:
                if self.append_mode:
                    # Check if order already exists
                    existing = conn.execute(
                        text("SELECT Id FROM Orders WHERE Id = :id"),
                        {"id": order["id"]},
                    ).fetchone()

                    if existing:
                        skipped_count += 1
                        continue
                # Insert order
                conn.execute(
                    text(
                        """
                    INSERT INTO Orders (
                        Id, UserId, OrderDate, Status, Subtotal, ShippingCost,
                        TaxAmount, TotalAmount, ShippingStreet, ShippingCity,
                        ShippingState, ShippingZipCode, ShippingCountry,
                        PaymentMethod, TrackingNumber
                    ) VALUES (
                        :id, :user_id, :order_date, :status, :subtotal, :shipping_cost,
                        :tax_amount, :total_amount, :shipping_street, :shipping_city,
                        :shipping_state, :shipping_zip_code, :shipping_country,
                        :payment_method, :tracking_number
                    )
                """
                    ),
                    {
                        "id": order["id"],
                        "user_id": order["user_id"],
                        "order_date": order["order_date"],
                        "status": order["status"],
                        "subtotal": order["totals"]["subtotal"],
                        "shipping_cost": order["totals"]["shipping_cost"],
                        "tax_amount": order["totals"]["tax_amount"],
                        "total_amount": order["totals"]["total"],
                        "shipping_street": order["shipping_address"]["street"],
                        "shipping_city": order["shipping_address"]["city"],
                        "shipping_state": order["shipping_address"]["state"],
                        "shipping_zip_code": order["shipping_address"]["postal_code"],
                        "shipping_country": order["shipping_address"]["country"],
                        "payment_method": order["payment_info"]["method"],
                        "tracking_number": order["shipping_info"]["tracking_number"],
                    },
                )

                # Insert order items
                for item in order["items"]:
                    conn.execute(
                        text(
                            """
                        INSERT INTO OrderItems (
                            OrderId, ProductId, ProductName, Quantity, UnitPrice, TotalPrice
                        ) VALUES (
                            :order_id, :product_id, :product_name, :quantity, :unit_price, :total_price
                        )
                    """
                        ),
                        {
                            "order_id": order["id"],
                            "product_id": item["product_id"],
                            "product_name": item["product_name"],
                            "quantity": item["quantity"],
                            "unit_price": item["unit_price"],
                            "total_price": item["total_price"],
                        },
                    )

                # Insert payment record
                conn.execute(
                    text(
                        """
                    INSERT INTO Payments (
                        OrderId, PaymentMethod, Amount, Status, TransactionId
                    ) VALUES (
                        :order_id, :payment_method, :amount, :status, :transaction_id
                    )
                """
                    ),
                    {
                        "order_id": order["id"],
                        "payment_method": order["payment_info"]["method"],
                        "amount": order["totals"]["total"],
                        "status": order["payment_info"]["status"],
                        "transaction_id": order["payment_info"]["transaction_id"],
                    },
                )
                inserted_count += 1

            conn.commit()

        if self.append_mode:
            print(
                f"Orders processed: {inserted_count} inserted, {skipped_count} skipped (already exist)"
            )
        else:
            print(f"Orders and payments inserted successfully: {inserted_count}")

    def create_indexes(self):
        """Create database indexes for better performance."""
        print("Creating indexes...")

        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            indexes = [
                "CREATE INDEX IX_Users_Email ON Users(Email)",
                "CREATE INDEX IX_Users_IsActive ON Users(IsActive)",
                "CREATE INDEX IX_Products_Category ON Products(CategoryId)",
                "CREATE INDEX IX_Products_IsActive ON Products(IsActive)",
                "CREATE INDEX IX_Products_Price ON Products(Price)",
                "CREATE INDEX IX_Orders_UserId ON Orders(UserId)",
                "CREATE INDEX IX_Orders_OrderDate ON Orders(OrderDate)",
                "CREATE INDEX IX_Orders_Status ON Orders(Status)",
                "CREATE INDEX IX_OrderItems_OrderId ON OrderItems(OrderId)",
                "CREATE INDEX IX_OrderItems_ProductId ON OrderItems(ProductId)",
                "CREATE INDEX IX_Payments_OrderId ON Payments(OrderId)",
            ]

            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"Warning: Could not create index: {e}")

            conn.commit()

        print("Indexes created successfully.")

    def populate_database(self):
        """Main method to populate the database with all data."""
        mode_text = "append mode" if self.append_mode else "recreate mode"
        print(f"Starting MSSQL database population ({mode_text})...")

        # Load data from shared_data directory
        data_dir = os.path.join("..", "shared_data")

        # print(os.path.abspath())
        print(os.getcwd())

        # Check if all required data files exist
        required_files = ["products.json", "users.json", "orders.json"]
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

        # Create database and tables
        self.create_database()

        # Insert data in correct order
        self.insert_categories(data["products"])
        category_mapping = self.get_category_mapping()

        self.insert_users(data["users"])
        self.insert_products(data["products"], category_mapping)
        self.insert_orders_and_items(data["orders"])

        # Create indexes for performance
        self.create_indexes()

        print("MSSQL database population completed successfully!")

        # Print summary
        engine = self.get_engine(self.db_name)
        with engine.connect() as conn:
            tables = [
                "Users",
                "Categories",
                "Products",
                "Orders",
                "OrderItems",
                "Payments",
            ]
            print(f"\nFinal record counts:")
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} records")


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Populate MSSQL database with e-commerce data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python populate_data.py                 # Recreate database (default)
    python populate_data.py --recreate      # Recreate database explicitly  
    python populate_data.py --append        # Add to existing database
        """,
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--recreate",
        action="store_true",
        default=True,
        help="Drop and recreate database, overwriting all data (default)",
    )
    mode_group.add_argument(
        "--append",
        action="store_true",
        help="Add new data to existing database, preserving existing records",
    )

    args = parser.parse_args()

    # Determine mode
    append_mode = args.append

    if append_mode:
        print("🔄 Running in APPEND mode - existing data will be preserved")
    else:
        print("🔄 Running in RECREATE mode - database will be recreated")
        print("⚠️  WARNING: This will destroy all existing data!")

    try:
        populator = MSSQLPopulator(append_mode=append_mode)
        populator.populate_database()

        if append_mode:
            print("✅ Database append completed successfully!")
        else:
            print("✅ Database recreation completed successfully!")

    except Exception as e:
        print(f"❌ Error populating MSSQL database: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
