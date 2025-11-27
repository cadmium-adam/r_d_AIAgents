import asyncio
import os
from datetime import datetime
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

# ---------------------------
# Define the graph
# ---------------------------


# State
class State(TypedDict):
    question: str
    current_date: datetime
    query: str
    search: str
    summarization: str



def DoSomethingNode(state: State):
    now = datetime.now()
    return {"current_date": now}


# Prepare query node
def PrepareQueryNode(state: State):
    print("PrepareQueryNode")
    print(state)

    messages = [
        {"role": "system", "content": "Improve the user query, so it can be used for a better search."},
        {"role": "user", "content": f"User question: {state['question']}, current Date: {datetime.now()}"},
    ]
    response = llm.invoke(messages)
    return {"query": response.content}


# API Call node (API call)
async def ApiCallNode(state: State):
    print("ApiCallNode")
    print(state)

    mcp_tools, mcp_client = await get_mcp_tools()
    # Use the tavily_search tool directly
    tavily_search = next(tool for tool in mcp_tools if "search" in tool.name.lower())
    search_result = await tavily_search.ainvoke({"query": state["query"]})
    return {"search": search_result}


# Summarize node (LLM call)
def SummarizeNode(state: State):
    print("SummarizeNode")
    messages = [
        {"role": "system", "content": "You are an AI assistant focused on summarizing!"},
        {"role": "user", "content": f"Summarize for me this information: \n\n ===\n{state['search']}\n==="},
    ]
    response = llm.invoke(messages)
    return {"summarization": response}


# Log node
def LogNode(state: State):
    print("LogNode")
    print(state)
    # return state
    pass


# Build the graph
builder = StateGraph(State)
builder.add_node("doSomething", DoSomethingNode)
builder.add_node("prepareQuery", PrepareQueryNode)
builder.add_node("apicall", ApiCallNode)
builder.add_node("summarize", SummarizeNode)
builder.add_node("log", LogNode)

builder.add_edge(START, "doSomething")
builder.add_edge("doSomething", "prepareQuery")
builder.add_edge("prepareQuery", "apicall")
builder.add_edge("apicall", "summarize")
builder.add_edge("summarize", "log")
builder.add_edge("log", END)

# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------


async def main():
    """Main async function to run the graph."""
    initial_state = {"question": "What are the latest news in AI?"}
    result = await graph.ainvoke(initial_state)
    print("--------- Result ---------")
    print(result["summarization"].content)


if __name__ == "__main__":
    asyncio.run(main())
