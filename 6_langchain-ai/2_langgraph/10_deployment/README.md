# LangGraph FastAPI Deployment

This project demonstrates how to deploy a LangGraph agent as a FastAPI service using the latest LangChain 1.0.2 API with Tavily MCP integration.

## Features

- FastAPI server with LangGraph agent integration
- Uses `create_agent` from `langchain.agents` (LangChain 1.0.2)
- **Tavily MCP integration** for real web search capabilities
- Custom tools: food ordering
- Session management for conversation history
- Health check endpoint
- Async agent invocation for better performance

## Setup

```bash
# Install dependencies
uv sync

# Create .env file with your API keys
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Running the Server

```bash
uv run python main.py
```

The server will start on http://localhost:8005

## API Endpoints

### Health Check
```bash
curl http://localhost:8005/health
```

### Chat with Agent
```bash
curl -X POST http://localhost:8005/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Can you get me a plate of spaghetti?"}'
```

### Test Web Search (Tavily MCP)
```bash
curl -X POST http://localhost:8005/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the latest news about AI?"}'
```

### With Session ID
```bash
curl -X POST http://localhost:8005/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I ask before?", "session_id": "test123"}'
```

### Get Session History
```bash
curl http://localhost:8005/sessions/{session_id}
```

### Clear Session
```bash
curl -X DELETE http://localhost:8005/sessions/{session_id}
```

## Technical Details

- **LangChain Version**: 1.0.2
- **LangGraph Version**: 1.0.2
- **Agent Function**: `create_agent` (from `langchain.agents`)
- **Model**: ChatOpenAI with `gpt-4o-mini`
- **MCP Integration**: `langchain-mcp-adapters` for Tavily search
- **System Prompt**: Configurable in agent.py:60
- **Agent Invocation**: Async (`ainvoke`)

## Architecture

The application uses:
1. **FastAPI** for the HTTP server
2. **LangGraph Agent** created with `create_agent`
3. **Tavily MCP Client** (`MultiServerMCPClient`) for web search tools
4. **Async initialization** on server startup to load MCP tools
5. **In-memory session storage** for conversation history

## Changes from Previous Version

1. ✅ Replaced `create_react_agent` with `create_agent`
2. ✅ Removed obsolete tools (ArxivQueryRun, WolframAlphaAPIWrapper, WolframAlphaQueryRun)
3. ✅ Replaced TavilySearchResults with **Tavily MCP** integration using `langchain-mcp-adapters`
4. ✅ Updated to use ChatOpenAI instance instead of string identifier
5. ✅ Updated to use `system_prompt` parameter
6. ✅ Added async agent initialization on server startup
7. ✅ Changed to async agent invocation (`ainvoke`) for better performance
