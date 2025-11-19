from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb://admin:admin123@localhost:27017/")

# Create / use database
db = client["mydatabase"]

# Collections
users = db["users"]
orders = db["orders"]

# Clear old data (optional)
users.delete_many({})
orders.delete_many({})

# ------------------------------
# CREATE
# ------------------------------

# Insert users
user1_id = users.insert_one({"name": "Alice", "email": "alice@example.com"}).inserted_id
user2_id = users.insert_one({"name": "Bob", "email": "bob@example.com"}).inserted_id

# Insert orders
orders.insert_many([
    {"user_id": user1_id, "product": "Laptop", "quantity": 1},
    {"user_id": user1_id, "product": "Mouse", "quantity": 2},
    {"user_id": user2_id, "product": "Keyboard", "quantity": 1}
])

# ------------------------------
# UPDATE
# ------------------------------

# Update order (e.g., change quantity of first order to 3)
orders.update_one({"product": "Laptop"}, {"$set": {"quantity": 3}})

# ------------------------------
# READ - SINGLE-COLLECTION SELECTS
# ------------------------------

print("\nAll users:")
for u in users.find():
    print(u)

print("\nAll orders:")
for o in orders.find():
    print(o)

print("\nOrders where quantity > 1:")
for o in orders.find({"quantity": {"$gt": 1}}):
    print(o)

print("\nOrders for product == 'Mouse':")
for o in orders.find({"product": "Mouse"}):
    print(o)

print("\nOnly 'product' and 'quantity' fields (projection):")
for o in orders.find({}, {"_id": 0, "product": 1, "quantity": 1}):
    print(o)

# ------------------------------
# READ - JOIN ($lookup)
# ------------------------------

print("Joined results (orders + user info):")
joined = orders.aggregate([
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    {"$unwind": "$user"},
    {
        "$project": {
            "_id": 0,
            "user_name": "$user.name",
            "email": "$user.email",
            "product": 1,
            "quantity": 1
        }
    }
])

for doc in joined:
    print(f"{doc['user_name']} ({doc['email']}) ordered {doc['quantity']} x {doc['product']}")


# ------------------------------
# DELETE
# ------------------------------

print("\n Deleting order for product == 'Mouse'")
delete_result = orders.delete_one({"product": "Mouse"})
print(f"Deleted {delete_result.deleted_count} document(s)")

print("\nOrders after delete:")
for o in orders.find():
    print(o)