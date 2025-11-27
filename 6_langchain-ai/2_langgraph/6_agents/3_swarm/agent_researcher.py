import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain.agents import create_agent
from visualizer import visualize
from handoff import transfer_to_summarizer
from langchain_mcp_adapters.client import MultiServerMCPClient

_ = load_dotenv(find_dotenv())  # read local .env file


async def get_research_mcp_tools():
    """Load tools from Tavily MCP server."""
    client = MultiServerMCPClient(
        {
            "tavily": {
                "transport": "streamable_http",
                "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv("TAVILY_API_KEY")}",
            },
            "arxiv": {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "tool",
                    "run",
                    "arxiv-mcp-server",
                    "--storage-path",
                    "/tmp/arxiv_papers",
                ],
            }
        }
    )
    tools = await client.get_tools()
    return tools, client



async def create_researcher_agent():
    """Create a researcher agent with access to web search tools."""

    # model
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

    # tools
    research_tools, _ = await get_research_mcp_tools()

    # agent
    researcher_agent = create_agent(
        model=llm,
        tools=research_tools + [transfer_to_summarizer],
        system_prompt="You are a web researcher. If you or any of the other assistants have the final answer or deliverable, prefix your response with [[[[FINAL ANSWER]]]] so the team knows to stop.",
        name="researcher",
    )

    # Visualize the agent graph
    # visualize(researcher_agent, "researcher_agent.png")

    return researcher_agent
