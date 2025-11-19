```bash
docker volume create qdrant_data

docker run -d --name qdrant -v qdrant_data:/data -p 6333:6333 qdrant/qdrant
```

UI - `http://localhost:6333/dashboard`

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
