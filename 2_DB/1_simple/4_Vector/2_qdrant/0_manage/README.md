ChromaDB does not have any Admin UI

```bash
uv run manage_qdrant.py list-collections
uv run manage_qdrant.py show-collection <collection_name>
uv run manage_qdrant.py collection-stats <collection_name>
uv run manage_qdrant.py health-check

 # basic collection (768 dimensions, Cosine)
uv run manage_qdrant.py create-collection my_collection

  # custom configuration
uv run manage_qdrant.py create-collection my_collection --vector-size 1536 --distance Euclidean

# With confirmation prompt
uv run manage_qdrant.py remove-collection my_collection

# Skip confirmation
uv run manage_qdrant.py remove-collection my_collection --force
```
