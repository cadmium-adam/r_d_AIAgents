from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Config
COLLECTION_NAME = "my_docs"

# Init Qdrant client and embedding model
qdrant_client = QdrantClient(host="localhost", port=6333)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔎 Semantic Search (type 'exit' to quit)")

while True:
    query = input("\n🧠 What are you looking for? ").strip()
    if query.lower() == "exit":
        break

    query_embedding = embedding_model.encode([query]).tolist()[0]
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=5
    )

    print("\n🎯 Top Matches:")
    for result in results:
        payload = result.payload
        score = result.score
        
        filename = payload.get("filename", "Unknown")
        text = payload.get("text", "")
        
        print(f"\n📄 File: {filename} (Score: {score:.3f})")
        print(f"→ {text[:300].replace(chr(10), ' ')}...")