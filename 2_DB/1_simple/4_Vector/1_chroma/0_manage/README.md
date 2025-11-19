ChromaDB does not have any Admin UI

```bash
uv run manage_chroma.py list-collections
uv run manage_chroma.py show-collection <collection_name>
uv run manage_chroma.py collection-stats <collection_name>
uv run manage_chroma.py health-check

# With confirmation prompt
uv run manage_chroma.py remove-collection my_collection

# Skip confirmation
uv run manage_chroma.py remove-collection my_collection --force
```
