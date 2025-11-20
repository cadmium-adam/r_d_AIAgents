# Prerequisities

1. Create a collection via Qdrant UI - `http://localhost:6333/dashboard`
   OR via terminal

```bash
curl -X PUT "http://localhost:6333/collections/n8n_test_data" \
  -H "Content-Type: application/json" \
  -d '{"vectors":{"size":384,"distance":"Cosine"}}'
```

# Steps

1. Fill the collection with data via workflow `3_4_1_Qdrant_InsertDocuments`

2. Retrieve collection data via `similarity search` with workflow `3_4_2_Qdrant_GetMany`
