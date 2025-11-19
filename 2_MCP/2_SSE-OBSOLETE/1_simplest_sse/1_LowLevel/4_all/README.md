# Run server

```bash
cd my_server

uv venv
source .venv/bin/activate
uv sync

uv run server.py

```

# Run client

```bash
cd my_client

uv venv
source .venv/bin/activate
uv sync

uv run main.py
```

# USE via Claude desktop

Add to the claude config

```JSON
IS NOT SUPPORTED YET
```

# USE via VSCode

Add to the VSCode

A) To the workspace (`.vscode/mcp.json`)
B) To the user settings to VSCode (`Ctrl + ,`)

```JSON
{
  "mcp": {
    "servers": {
      "mysimplesse": {
        "type": "sse",
        "url": "http://localhost:8001/sse",
        "headers": { "VERSION": "1.2" }
      }
    }
  }
}
```
