import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from visualizer import visualize
from langgraph.graph import START, END
from langchain_mcp_adapters.client import MultiServerMCPClient

_ = load_dotenv(find_dotenv())  # read local .env file


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


# Global variable to store LLM with search tools
llm_with_search = None

# ---------------------------
# Define the graph
# ---------------------------


# State
class State(TypedDict):
    theme: str
    jokeText: str
    storyText: str
    memeText: str


# Joke node
def JokeNode(state: State):
    messages = [
        {"role": "system", "content": "You are a hilarious person!"},
        {"role": "user", "content": f"Generate a joke on theme: {state['theme']}"},
    ]
    response = llm.invoke(messages)
    return {"jokeText": response}


# Story node
def StoryNode(state: State):
    messages = [
        {"role": "system", "content": "You are a storyteller!"},
        {"role": "user", "content": f"Generate a story for theme: {state['theme']}"},
    ]
    response = llm.invoke(messages)
    return {"storyText": response}


# Meme node - uses Tavily MCP to search for memes
def MemeNode(state: State):
    global llm_with_search

    messages = [
        {"role": "system", "content": "You are a meme searcher!"},
        {"role": "user", "content": f"Find a meme for theme: {state['theme']}"},
    ]
    response = llm_with_search.invoke(messages)
    return {"memeText": response}


# Build the graph
builder = StateGraph(State)
builder.add_node("joke", JokeNode)
builder.add_node("story", StoryNode)
builder.add_node("meme", MemeNode)

builder.add_edge(START, "joke")
builder.add_edge("joke", "story")
builder.add_edge("story", "meme")
builder.add_edge("meme", END)

# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------


async def main():
    """Main async function to run the graph."""
    global llm_with_search

    # Initialize MCP tools
    print("Initializing MCP connection to Tavily...")
    mcp_tools, mcp_client = await get_mcp_tools()
    print(f"Loaded {len(mcp_tools)} tools from Tavily MCP\n")

    # Bind tools to LLM
    llm_with_search = llm.bind_tools(mcp_tools)

    theme = "space"
    initial_state = {"jokeText": "", "storyText": "", "memeText": "", "theme": theme}
    result = graph.invoke(initial_state)
    print("JOKE:")
    print(result["jokeText"].content)
    print("\nSTORY:")
    print(result["storyText"].content)
    print("\nMEME:")
    print(result["memeText"])


if __name__ == "__main__":
    asyncio.run(main())
