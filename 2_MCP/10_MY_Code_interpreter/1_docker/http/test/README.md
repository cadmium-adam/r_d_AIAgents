# HTTP MCP Server Tests

Tests for the HTTP streaming MCP Python executor server.

## Prerequisites

1. **Start the HTTP MCP Server**:
   ```bash
   # From the http directory
   cd ..
   docker-compose --profile http up -d

   # Or run directly
   python mcp_python_server.py
   ```

2. **Install test dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

### Run all tests
```bash
python main.py
```

### Run specific test suites

**Simple Python tests** (basic execution, no dependencies):
```bash
python main.py simple
```

**Streaming tests** (Server-Sent Events):
```bash
python main.py stream
```

**Dependency tests** (install and use packages):
```bash
python main.py deps
```

**Quick test** (basic health check):
```bash
python main.py quick
```

## Test Structure

1. **test_simple_python()** - Tests basic Python execution:
   - Basic print and arithmetic
   - Functions and loops
   - Built-in modules (datetime, random, math, json)
   - Error handling

2. **test_streaming()** - Tests SSE streaming:
   - Real-time event streaming
   - Progress updates during execution

3. **test_with_dependencies()** - Tests package installation:
   - Install and use `requests` library
   - Install and use `pandas` and `numpy`
   - Data analysis operations
   - List installed packages

## Key Differences from stdio Tests

- Uses HTTP requests instead of stdio communication
- Includes streaming tests with Server-Sent Events (SSE)
- Uses `aiohttp` for async HTTP client
- Tests health check endpoint
- Tests tool listing endpoint
- Can run against remote servers (change `base_url`)

## Customization

To test against a different server:

```python
async with MCPHTTPClient(base_url="http://your-server:8000") as client:
    # your tests
```
