import os
import uuid
import chromadb
from chromadb.utils import embedding_functions

# Config
SOURCE_DIR = "source"
COLLECTION_NAME = "my_docs"
MAX_CHUNK_LEN = 2048

# Chroma client and embedding
chroma_client = chromadb.HttpClient(host="localhost", port=8100)
embedding = embedding_functions.DefaultEmbeddingFunction()

# Delete existing collection if it exists
existing = [c.name for c in chroma_client.list_collections()]
if COLLECTION_NAME in existing:
    chroma_client.delete_collection(name=COLLECTION_NAME)

# Create collection
collection = chroma_client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding,
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
for filename in os.listdir(SOURCE_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    chunks = split_document(content, max_length=MAX_CHUNK_LEN)
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"filename": filename} for _ in chunks]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"✅ Added {len(chunks)} chunks from {filename}")

print(f"✅ Indexed documents from folder: {SOURCE_DIR}")
print(f"Total documents in collection: {collection.count()}")
