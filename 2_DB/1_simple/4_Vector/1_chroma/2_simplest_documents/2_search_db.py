import chromadb
from chromadb.utils import embedding_functions

# Config
COLLECTION_NAME = "my_docs"

# Init Chroma client and collection
chroma_client = chromadb.HttpClient(host="localhost", port=8100)
embedding = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)

print("🔎 Semantic Search (type 'exit' to quit)")
print(f"Collection has {collection.count()} documents")

while True:
    query = input("\n🧠 What are you looking for? ").strip()
    if query.lower() == "exit":
        break

    results = collection.query(query_texts=[query], n_results=5)

    if not results["documents"][0]:
        print("❌ No results found")
        continue

    print("\n🎯 Top Matches:")
    for i in range(len(results["documents"][0])):
        document = results["documents"][0][i]
        meta = results.get("metadatas", [[None]])[0][i]

        filename = meta.get("filename", "Unknown") if meta else "Unknown"
        print(f"\n📄 File: {filename}")
        print(f"→ {document[:300].replace(chr(10), ' ')}...")
