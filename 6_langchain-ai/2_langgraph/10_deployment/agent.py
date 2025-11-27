import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

# Model
llm = ChatOpenAI(model="gpt-4o-mini")


# ============================================================================
# MCP CLIENT SETUP
# ============================================================================


def get_tavily_mcp_url():
    """Get Tavily MCP URL with API key."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    return f"https://mcp.tavily.com/mcp/?tavilyApiKey={api_key}"


async def get_mcp_tools():
    """Load tools from Tavily MCP server."""
    client = MultiServerMCPClient(
        {
            "tavily": {
                "url": get_tavily_mcp_url(),
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()
    return tools, client


@tool
def get_food() -> str:
    """Get a plate of spaghetti."""
    return "Here is your plate of spaghetti 🍝"


async def create_agent_graph():
    """Create the agent graph with MCP tools."""
    # Initialize MCP tools
    mcp_tools, mcp_client = await get_mcp_tools()

    # Combine all tools
    tools = list(mcp_tools) + [get_food]

    # Create agent
    agent = create_agent(
        llm,
        tools=tools,
        system_prompt="You are a helpful assistant. Be concise and accurate.",
    )

    return agent


# Initialize agent graph synchronously for FastAPI
# Note: This will be called asynchronously when the server starts
agent_graph = None
