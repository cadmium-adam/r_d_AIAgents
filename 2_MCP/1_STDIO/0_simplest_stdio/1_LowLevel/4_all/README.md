# RUN via client

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
{
  "mcpServers": {
    "mysimplestdin": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "/home/lukas/.local/bin/uv --directory /home/lukas/Projects/Github/lukaskellerstein/ai/15_MCP/0_simplest_stdio/1_LowLevel/4_all/my_server run server.py"
      ]
    }
  }
}

```

# USE via VSCode

Add to the VSCode

A) To the workspace (`.vscode/mcp.json`)
B) To the user settings to VSCode (`Ctrl + ,`)

```JSON
{
  "mcp": {
    "servers": {
      "mysimplestdin": {
        "type": "stdio",
        "command": "wsl.exe",
        "args": [
            "bash",
            "-c",
            "/home/lukas/.local/bin/uv --directory /home/lukas/Projects/Github/lukaskellerstein/ai/15_MCP/0_simplest_stdio/1_LowLevel/4_all/my_server run server.py"
        ]
      }
    }
  }
}
```
