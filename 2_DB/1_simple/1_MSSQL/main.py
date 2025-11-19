import pyodbc

# Connection config
server = "localhost"
database = "MyDatabase"
username = "sa"
password = "Heslo_1234"
driver = "{ODBC Driver 18 for SQL Server}"

# Connect to master to ensure DB exists
conn_master = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE=master;UID={username};PWD={password};Encrypt=no",
    autocommit=True,
)
cursor_master = conn_master.cursor()
cursor_master.execute(
    f"""
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{database}')
    CREATE DATABASE [{database}]
"""
)
print(f"Database '{database}' ensured.")

# Connect to target DB
conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=no",
    autocommit=True,
)
cursor = conn.cursor()

# ------------------------------
# SETUP: Drop & Create Tables
# ------------------------------
cursor.execute("IF OBJECT_ID('Orders', 'U') IS NOT NULL DROP TABLE Orders")
cursor.execute("IF OBJECT_ID('Users', 'U') IS NOT NULL DROP TABLE Users")

cursor.execute(
    """
CREATE TABLE Users (
    Id INT IDENTITY PRIMARY KEY,
    Name NVARCHAR(100),
    Email NVARCHAR(100)
)
"""
)

cursor.execute(
    """
CREATE TABLE Orders (
    Id INT IDENTITY PRIMARY KEY,
    UserId INT FOREIGN KEY REFERENCES Users(Id),
    Product NVARCHAR(100),
    Quantity INT
)
"""
)

# ------------------------------
# CREATE
# ------------------------------

# Insert users
cursor.execute(
    "INSERT INTO Users (Name, Email) VALUES (?, ?)", "Alice", "alice@example.com"
)
cursor.execute(
    "INSERT INTO Users (Name, Email) VALUES (?, ?)", "Bob", "bob@example.com"
)

# Get inserted user IDs
cursor.execute("SELECT Id FROM Users WHERE Name = 'Alice'")
user1_id = cursor.fetchone()[0]

cursor.execute("SELECT Id FROM Users WHERE Name = 'Bob'")
user2_id = cursor.fetchone()[0]

# Insert orders
cursor.execute(
    "INSERT INTO Orders (UserId, Product, Quantity) VALUES (?, ?, ?)",
    user1_id,
    "Laptop",
    1,
)
cursor.execute(
    "INSERT INTO Orders (UserId, Product, Quantity) VALUES (?, ?, ?)",
    user1_id,
    "Mouse",
    2,
)
cursor.execute(
    "INSERT INTO Orders (UserId, Product, Quantity) VALUES (?, ?, ?)",
    user2_id,
    "Keyboard",
    1,
)

# ------------------------------
# UPDATE
# ------------------------------

cursor.execute("UPDATE Orders SET Quantity = ? WHERE Product = ?", 3, "Laptop")

# ------------------------------
# READ - SINGLE-TABLE SELECTS
# ------------------------------

print("\nAll users:")
cursor.execute("SELECT * FROM Users")
for row in cursor.fetchall():
    print(row)

print("\nAll orders:")
cursor.execute("SELECT * FROM Orders")
for row in cursor.fetchall():
    print(row)

print("\nOrders where quantity > 1:")
cursor.execute("SELECT * FROM Orders WHERE Quantity > 1")
for row in cursor.fetchall():
    print(row)

print("\nOrders for product == 'Mouse':")
cursor.execute("SELECT * FROM Orders WHERE Product = 'Mouse'")
for row in cursor.fetchall():
    print(row)

print("\nOnly 'product' and 'quantity' fields (projection):")
cursor.execute("SELECT Product, Quantity FROM Orders")
for row in cursor.fetchall():
    print(row)

# ------------------------------
# READ - JOIN
# ------------------------------

print("\nJoined results (orders + user info):")
cursor.execute(
    """
SELECT 
    u.Name AS UserName,
    u.Email,
    o.Product,
    o.Quantity
FROM Orders o
JOIN Users u ON o.UserId = u.Id
"""
)
for row in cursor.fetchall():
    print(f"{row.UserName} ({row.Email}) ordered {row.Quantity} x {row.Product}")

# ------------------------------
# DELETE
# ------------------------------

print("\nDeleting order for product == 'Mouse'")
cursor.execute("DELETE FROM Orders WHERE Product = 'Mouse'")
print(f"Deleted {cursor.rowcount} row(s)")

print("\nOrders after delete:")
cursor.execute("SELECT * FROM Orders")
for row in cursor.fetchall():
    print(row)
