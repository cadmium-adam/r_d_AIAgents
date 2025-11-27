from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def main():

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

    mcp_tools, mcp_client = await get_mcp_tools()

    # model
    llm = ChatOpenAI(model="gpt-4.1-mini")

    # agent
    agent = create_agent(
        llm,
        tools=mcp_tools,
        system_prompt="You are a helpful assistant.",
    )

    conversation = {
        "messages": [
            {
                "role": "user",
                "content": "What is the current price of MSFT stock?",
            },
        ]
    }

    # # call model
    # res = await agent.ainvoke(conversation)
    # print("---- Response ----")
    # print(res)

    # streaming
    async for chunk in agent.astream(
        conversation,
        stream_mode="messages",
    ):

        message, metadata = chunk

        print(f"\n{'='*60}")
        print(f"Node: {metadata.get('langgraph_node', 'unknown')}")
        print(f"{'='*60}")

        # Log message type
        print(f"Type: {type(message).__name__}")

        # Log content
        if hasattr(message, "content") and message.content:
            print(f"Content: {message.content}")

        # Log tool calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            print("\nTool Calls:")
            for tool_call in message.tool_calls:
                print(f"  - {tool_call['name']}({tool_call['args']})")

        # Log tool response
        if isinstance(message, ToolMessage):
            print(f"Tool Result: {message.content[:200]}...")  # truncate long responses


if __name__ == "__main__":
    asyncio.run(main())
