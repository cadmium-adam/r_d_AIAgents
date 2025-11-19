import chromadb
from sentence_transformers import SentenceTransformer


# --- Setup ---
model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.HttpClient(host="localhost", port=8100)

collection_name = "products"

# Recreate collection
# Check and delete collection if it exists
existing = [c.name for c in chroma_client.list_collections()]
if collection_name in existing:
    chroma_client.delete_collection(name=collection_name)

collection = chroma_client.create_collection(name=collection_name)

# --- Sample product data ---
products = [
    {
        "id": "1",
        "title": "Wireless Bluetooth Headphones",
        "description": "Over-ear noise-cancelling headphones with 20h battery life",
    },
    {
        "id": "2",
        "title": "Gaming Laptop",
        "description": "High-performance laptop with RTX 3060 GPU and 16GB RAM for gaming and content creation",
    },
    {
        "id": "3",
        "title": "Eco-Friendly Water Bottle",
        "description": "Reusable stainless steel bottle made from recycled materials, keeps drinks cold for 24h",
    },
    {
        "id": "4",
        "title": "Fitness Tracker Watch",
        "description": "Tracks steps, heart rate, and sleep with 7-day battery and waterproof design",
    },
    {
        "id": "5",
        "title": "Smart Home Security Camera",
        "description": "1080p WiFi indoor camera with motion detection and mobile alerts",
    },
    {
        "id": "6",
        "title": "Hiking Backpack",
        "description": "Water-resistant backpack with 35L capacity, suitable for mountain trips",
    },
    {
        "id": "7",
        "title": "Mechanical Keyboard",
        "description": "RGB backlit mechanical keyboard with tactile switches, perfect for gamers",
    },
    {
        "id": "8",
        "title": "Noise-Isolating Earbuds",
        "description": "Compact in-ear headphones with rich bass and passive noise isolation",
    },
    {
        "id": "9",
        "title": "4K Monitor",
        "description": "Ultra HD 27-inch monitor with HDR support and slim bezel design",
    },
    {
        "id": "10",
        "title": "Portable Solar Charger",
        "description": "Foldable solar charger with USB-C output for phones and tablets on the go",
    },
]

# Prepare and insert
texts = [p["title"] + ". " + p["description"] for p in products]
ids = [p["id"] for p in products]
metadatas = [{"title": p["title"]} for p in products]
embeddings = model.encode(texts).tolist()

collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)

print("✅ Product data inserted into Chroma DB.")
