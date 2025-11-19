```bash
docker volume create chroma_data

docker run -d --name chromadb -v chroma_data:/data -p 8100:8000 chromadb/chroma
```

```python
import chromadb
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
```

# Run

## Run directly

`uv run main.py` (or alternative files)

## Run indirectly

Create a virtual environment

```bash
uv venv
```

Activate virtual environment

```bash
source .venv/bin/activate
```

Install packages

```bash
uv sync
```

Run script main (or alternative files)

```bash
python main.py
```
