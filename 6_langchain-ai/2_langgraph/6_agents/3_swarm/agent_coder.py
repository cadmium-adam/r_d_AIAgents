from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
from langchain.agents import create_agent
from visualizer import visualize
from handoff import transfer_to_summarizer
from langchain_mcp_adapters.client import MultiServerMCPClient


_ = load_dotenv(find_dotenv())  # read local .env file


async def create_coder_agent():
    """Create a coder agent with access to a Python REPL tool."""

    async def get_coder_mcp_tools():
        """Load tools from Tavily MCP server."""
        client = MultiServerMCPClient(
            {
                "python": {
                    "transport": "streamable_http",
                    "url": f"http://localhost:8056/mcp/",
                }
            }
        )
        tools = await client.get_tools()
        return tools, client

    # model
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

    # tools
    coder_tools, _ = await get_coder_mcp_tools()

    # agent
    coder_agent = create_agent(
        model=llm,
        tools=coder_tools + [transfer_to_summarizer],
        system_prompt="You are a coder, you can write any code, prefered language is Python. If you or any of the other assistants have the final answer or deliverable, prefix your response with [[[[FINAL ANSWER]]]] so the team knows to stop.",
        name="coder",
    )

    # Visualize the agent graph
    # visualize(coder_agent, "coder_agent.png")

    return coder_agent
