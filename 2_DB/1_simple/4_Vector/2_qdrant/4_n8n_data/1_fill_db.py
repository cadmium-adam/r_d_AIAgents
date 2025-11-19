from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer


# --- Setup ---
model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant_client = QdrantClient(host="localhost", port=6333)

collection_name = "n8n_simplest_products"

# Recreate collection
# Check and delete collection if it exists
collections = qdrant_client.get_collections()
existing_names = [c.name for c in collections.collections]
if collection_name in existing_names:
    qdrant_client.delete_collection(collection_name=collection_name)

qdrant_client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# --- Sample N8N data ---
# This mimics the data structure that comes from N8N with "content" and "metadata" fields
n8n_data = [
    {
        "content": "Wireless Bluetooth Headphones with over-ear noise-cancelling technology and 20h battery life for premium audio experience",
        "metadata": {
            "id": "1",
            "title": "Wireless Bluetooth Headphones",
            "description": "Over-ear noise-cancelling headphones with 20h battery life",
        },
    },
    {
        "content": "High-performance Gaming Laptop equipped with RTX 3060 GPU and 16GB RAM designed for gaming and content creation tasks",
        "metadata": {
            "id": "2",
            "title": "Gaming Laptop",
            "description": "High-performance laptop with RTX 3060 GPU and 16GB RAM for gaming and content creation",
        },
    },
    {
        "content": "Eco-Friendly Water Bottle made from recycled stainless steel materials that keeps drinks cold for 24 hours",
        "metadata": {
            "id": "3",
            "title": "Eco-Friendly Water Bottle",
            "description": "Reusable stainless steel bottle made from recycled materials, keeps drinks cold for 24h",
        },
    },
    {
        "content": "Fitness Tracker Watch that monitors steps, heart rate, and sleep patterns with 7-day battery life and waterproof design",
        "metadata": {
            "id": "4",
            "title": "Fitness Tracker Watch",
            "description": "Tracks steps, heart rate, and sleep with 7-day battery and waterproof design",
        },
    },
    {
        "content": "Smart Home Security Camera with 1080p WiFi connectivity featuring motion detection and mobile alert notifications",
        "metadata": {
            "id": "5",
            "title": "Smart Home Security Camera",
            "description": "1080p WiFi indoor camera with motion detection and mobile alerts",
        },
    },
    {
        "content": "Hiking Backpack with water-resistant design and 35L capacity perfect for mountain hiking trips and outdoor adventures",
        "metadata": {
            "id": "6",
            "title": "Hiking Backpack",
            "description": "Water-resistant backpack with 35L capacity, suitable for mountain trips",
        },
    },
    {
        "content": "Mechanical Keyboard with RGB backlighting and tactile switches designed specifically for gaming enthusiasts",
        "metadata": {
            "id": "7",
            "title": "Mechanical Keyboard",
            "description": "RGB backlit mechanical keyboard with tactile switches, perfect for gamers",
        },
    },
    {
        "content": "Noise-Isolating Earbuds featuring compact in-ear design with rich bass sound and passive noise isolation technology",
        "metadata": {
            "id": "8",
            "title": "Noise-Isolating Earbuds",
            "description": "Compact in-ear headphones with rich bass and passive noise isolation",
        },
    },
    {
        "content": "4K Monitor with Ultra HD 27-inch display featuring HDR support and modern slim bezel design for professionals",
        "metadata": {
            "id": "9",
            "title": "4K Monitor",
            "description": "Ultra HD 27-inch monitor with HDR support and slim bezel design",
        },
    },
    {
        "content": "Portable Solar Charger with foldable design and USB-C output perfect for charging phones and tablets while traveling",
        "metadata": {
            "id": "10",
            "title": "Portable Solar Charger",
            "description": "Foldable solar charger with USB-C output for phones and tablets on the go",
        },
    },
]

# Prepare and insert
# Extract content (text) for embedding generation
texts = [item["content"] for item in n8n_data]
embeddings = model.encode(texts).tolist()

points = []
for i, item in enumerate(n8n_data):
    points.append(
        PointStruct(
            id=int(item["metadata"]["id"]),
            vector=embeddings[i],
            payload={
                "content": item["content"],  # Store the full content text
                "metadata": {
                    "id": item["metadata"]["id"],
                    "title": item["metadata"]["title"],
                    "description": item["metadata"]["description"],
                },
            },
        )
    )

qdrant_client.upsert(collection_name=collection_name, points=points)

print("✅ N8N data inserted into Qdrant.")
