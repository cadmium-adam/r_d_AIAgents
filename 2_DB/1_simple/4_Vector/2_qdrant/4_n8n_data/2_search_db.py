# search_n8n_data_qdrant.py

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# --- Setup ---
model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant_client = QdrantClient(host="localhost", port=6333)

collection_name = "n8n_simplest_products"

# --- Search loop ---
print("🔎 Semantic N8N Data Search (type 'exit' to quit)")

while True:
    query = input("\n🧠 What are you looking for? ").strip()
    if query.lower() == "exit":
        break

    query_embedding = model.encode([query]).tolist()[0]
    results = qdrant_client.search(
        collection_name=collection_name, query_vector=query_embedding, limit=5
    )

    print("\n🎯 Top Matches:")
    for result in results:
        metadata = result.payload["metadata"]
        id = metadata["id"]
        title = metadata["title"]
        description = metadata["description"]
        content = result.payload["content"]
        score = result.score

        print(f"• ID: {id} | {title} (score: {score:.3f})")
        print(f"  Description: {description}")
        print(f"  Content: {content}")
        print("  " + "-" * 60)
