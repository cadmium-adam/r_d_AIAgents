from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

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

    # tools
    research_tools, _ = await get_research_mcp_tools()

    # model
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

    # agent
    researcher_agent = create_agent(
        model=llm,  
        tools=research_tools,  
        system_prompt="You are a web researcher. If you or any of the other assistants have the final answer or deliverable, prefix your response with [[[[FINAL ANSWER]]]] so the team knows to stop."  
    )

    return researcher_agent
