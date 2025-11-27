# Agent as Tool - Tool Calling Pattern

This example demonstrates the **tool calling** pattern where one agent (the "controller") treats other agents as tools to be invoked when needed.

## Pattern Overview

In tool calling:
1. The **controller agent** receives input and decides which tool (subagent) to call
2. The **tool agent** (subagent) runs its task based on the controller's instructions
3. The **tool agent** returns results to the controller
4. The **controller** decides the next step or finishes

```
User → Controller Agent → Tool Agent 1 → Controller Agent → User Response
                       → Tool Agent 2 ↗
```

## Key Characteristics

- **Controller manages orchestration**: The main agent decides when and how to use subagents
- **Subagents are tools**: They perform specific tasks and return results
- **No user conversation**: Subagents generally don't continue conversation with users
- **Results flow back**: All outputs return to the controller for further processing

## Implementation Details

### MCP Integration

This example uses **Model Context Protocol (MCP)** to connect to Tavily's remote search service:

- **Remote MCP Server**: Tavily provides a remote MCP server at `https://mcp.tavily.com/mcp/`
- **LangChain MCP Adapters**: Uses `langchain-mcp-adapters` to convert MCP tools into LangChain tools
- **SSE Transport**: Connects to the remote server using Server-Sent Events (SSE) transport

### Subagents

This example includes two specialized subagents:

1. **Research Agent**: Uses Tavily MCP tools for web search
   - Connects to Tavily's remote MCP server
   - Uses `tavily_search` tool from MCP
   - Synthesizes search results into clear answers

2. **Calculator Agent**: Performs mathematical calculations
   - Local tool implementation
   - Evaluates Python mathematical expressions
   - Returns formatted results

### Controller Agent

The controller agent has access to both subagents via tool wrappers and decides which to invoke based on the user's query.

## Customization Points

You can control the agent interaction at several points:

1. **Subagent name**: How the controller refers to the subagent (affects prompting)
2. **Subagent description**: What the controller "knows" about the subagent (shapes when to call it)
3. **Input to subagent**: Customize what context/data is passed to the subagent
4. **Output from subagent**: Control what results are returned to the controller

## Setup

1. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
```

2. Install dependencies:
```bash
uv sync
```

## Usage

Run the example:
```bash
uv run python main.py
```

The example demonstrates:
- Simple tool invocation (calculator)
- Research task delegation (web search via MCP)
- Controller orchestration of multiple subagents
- Async execution with proper MCP client cleanup

## Architecture

```
┌─────────────────────────────────────────┐
│       Controller Agent (GPT-4o)         │
│  - Orchestrates subagent invocations    │
│  - Decides which tool to use            │
└──────────┬──────────────────────┬───────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌─────────────────────┐
│  Research Agent  │   │  Calculator Agent   │
│  (GPT-4o-mini)   │   │   (GPT-4o-mini)     │
└────────┬─────────┘   └──────────┬──────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌──────────────────┐
│  Tavily MCP     │     │  calculate tool  │
│  (Remote SSE)   │     │  (Local Python)  │
└─────────────────┘     └──────────────────┘
```

## Key Features

- **MCP Remote Connection**: Demonstrates how to connect to remote MCP servers (Tavily)
- **Tool Wrapping**: Shows how to wrap agents as tools for the controller
- **Async Support**: Full async/await support for efficient execution
- **Clean Resource Management**: Proper MCP client cleanup after use
