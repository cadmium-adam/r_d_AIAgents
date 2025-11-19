import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Config
SOURCE_DIR = "source"
COLLECTION_NAME = "my_docs"
MAX_CHUNK_LEN = 2048

# Qdrant client and embedding model
qdrant_client = QdrantClient(host="localhost", port=6333)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Create or recreate collection
collections = qdrant_client.get_collections()
existing_names = [c.name for c in collections.collections]
if COLLECTION_NAME in existing_names:
    qdrant_client.delete_collection(collection_name=COLLECTION_NAME)

qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)


def split_document(text, max_length=2048):
    """Split a long text into chunks of ~max_length characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = len(word)
        else:
            current_chunk.append(word)
            current_len += len(word) + 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


# Process all .txt files in source/
all_points = []
point_id = 0

for filename in os.listdir(SOURCE_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    chunks = split_document(content, max_length=MAX_CHUNK_LEN)
    embeddings = embedding_model.encode(chunks)

    for i, chunk in enumerate(chunks):
        all_points.append(
            PointStruct(
                id=point_id,
                vector=embeddings[i].tolist(),
                payload={"filename": filename, "text": chunk, "chunk_id": i},
            )
        )
        point_id += 1

qdrant_client.upsert(collection_name=COLLECTION_NAME, points=all_points)

print(f"✅ Indexed documents from folder: {SOURCE_DIR}")
