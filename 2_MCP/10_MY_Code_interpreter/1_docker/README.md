# MCP Python Executor

A Model Context Protocol (MCP) server that provides Python code execution capabilities with two transport options: stdio and HTTP streaming.

## Project Structure

```
10_MY_Code_interpreter/
├── stdio/                      # stdio transport version
│   ├── mcp_python_server.py   # stdio MCP server
│   ├── requirements.txt        # stdio dependencies
│   ├── Dockerfile             # stdio container config
│   └── test/                  # test files
├── http/                       # HTTP transport version
│   ├── mcp_python_server.py   # HTTP MCP server with SSE
│   ├── requirements.txt        # HTTP dependencies (includes uvicorn, starlette)
│   ├── Dockerfile             # HTTP container config
│   └── test/                  # test files
├── docker-compose.yml          # Orchestration for both versions
└── README.md                   # This file
```

## Features

- Execute Python code in an isolated environment
- Install Python packages dynamically
- List installed packages
- Two transport modes: stdio and HTTP streaming

## Quick Start

### Option A: stdio Transport (Original)

For direct process communication via stdin/stdout.

**Build:**

```bash
cd stdio
docker build -t mcp-python-executor:stdio .
```

**Run interactively:**

```bash
docker run -it mcp-python-executor:stdio
```

**Run as daemon:**

```bash
docker run -d --name python-executor-stdio lukaskellerstein/mcp-python-executor:stdio
```

**Push:**

```bash
docker tag mcp-python-executor:stdio lukaskellerstein/mcp-python-executor:stdio
docker push lukaskellerstein/mcp-python-executor:stdio
```

### Option B: HTTP Streaming Transport (Recommended for Long-Running Containers)

For HTTP-based communication with Server-Sent Events (SSE) streaming.

**Build:**

```bash
cd http
docker build -t mcp-python-executor:http .
```

**Run:**

```bash
docker run -d -p 8055:8055 --name python-executor-http lukaskellerstein/mcp-python-executor:http
```

**Push:**

```bash
docker tag mcp-python-executor:http lukaskellerstein/mcp-python-executor:http
docker push lukaskellerstein/mcp-python-executor:http
```

## Docker Compose (Recommended)

Use docker-compose for easier management from the root directory:

**Run stdio version:**

```bash
docker-compose --profile stdio up -d
```

**Run HTTP version:**

```bash
docker-compose --profile http up -d
```

**Build and run:**

```bash
docker-compose --profile http up --build -d
```

**Stop:**

```bash
docker-compose --profile http down
# or
docker-compose --profile stdio down
```

## HTTP API Endpoints

When using the HTTP transport (`http/mcp_python_server.py`):

### Health Check

```bash
curl http://localhost:8000/health
```

### List Available Tools

```bash
curl http://localhost:8000/tools
```

### Execute Tool (Standard Response)

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "execute_python",
    "arguments": {
      "code": "print(\"Hello from MCP!\")"
    }
  }'
```

### Execute Tool (Streaming Response with SSE)

```bash
curl -X POST http://localhost:8000/execute/stream \
  -H "Content-Type: application/json" \
  -d '{
    "name": "execute_python",
    "arguments": {
      "code": "import time\nfor i in range(5):\n    print(f\"Count: {i}\")\n    time.sleep(1)"
    }
  }'
```

### Install Dependencies

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "install_dependencies",
    "arguments": {
      "packages": ["requests", "numpy"]
    }
  }'
```

### List Installed Packages

```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_installed_packages",
    "arguments": {}
  }'
```

## Available Tools

1. **execute_python** - Execute Python code

   - Input: `code` (string) - Python code to execute
   - Returns: stdout, stderr, and exit code

2. **install_dependencies** - Install Python packages via pip

   - Input: `packages` (array of strings) - Package names to install
   - Returns: Installation status for each package

3. **list_installed_packages** - List currently installed packages
   - Input: None
   - Returns: List of installed packages with versions

## Architecture

### stdio Transport

- Uses MCP's stdio transport for direct process communication
- Best for: Local development, direct tool integration
- Directory: `stdio/`
- File: `stdio/mcp_python_server.py`

### HTTP Streaming Transport

- Uses HTTP with Server-Sent Events (SSE) for streaming responses
- Best for: Long-running containers, network-accessible services, production deployments
- Directory: `http/`
- File: `http/mcp_python_server.py`
- Endpoints:
  - `GET /health` - Health check
  - `GET /tools` - List available tools
  - `POST /execute` - Execute tool (standard JSON response)
  - `POST /execute/stream` - Execute tool (SSE streaming response)

## Development

### Local Testing (HTTP version)

```bash
# Navigate to http directory
cd http

# Install dependencies
pip install -r requirements.txt

# Run server
python mcp_python_server.py

# In another terminal, test
curl http://localhost:8000/health
```

### Local Testing (stdio version)

```bash
# Navigate to stdio directory
cd stdio

# Install dependencies
pip install -r requirements.txt

# Run server
python mcp_python_server.py
```

## Security Considerations

- Runs as non-root user in container
- Code execution is sandboxed within the container
- 30-second timeout for code execution
- 60-second timeout for package installation
- HTTP version includes health checks

## When to Use Which Transport?

**Use stdio when:**

- Running locally or in development
- Direct process-to-process communication
- Using with MCP client tools that expect stdio

**Use HTTP streaming when:**

- Deploying as a long-running service
- Need network accessibility
- Want health checks and monitoring
- Running in production
- Need to access from multiple clients
- Want to use standard HTTP tools and load balancers
