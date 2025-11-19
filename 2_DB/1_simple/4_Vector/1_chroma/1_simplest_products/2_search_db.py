# search_products_chroma.py

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# --- Setup ---
model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.HttpClient(host="localhost", port=8100)

collection = chroma_client.get_collection("products")

# --- Search loop ---
print("🔎 Semantic Product Search (type 'exit' to quit)")

while True:
    query = input("\n🧠 What are you looking for? ").strip()
    if query.lower() == "exit":
        break

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=5)

    print("\n🎯 Top Matches:")
    for i in range(len(results["documents"][0])):
        title = results["metadatas"][0][i]["title"]
        desc = results["documents"][0][i]
        print(f"• {title} → {desc}")
