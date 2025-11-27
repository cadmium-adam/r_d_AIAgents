from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def main():

    client = MultiServerMCPClient(
        {
            "playwright": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
            },
        }
    )

    tools = await client.get_tools(server_name="playwright")

    # model
    llm = ChatOpenAI(model="gpt-5-nano")

    llm_with_tools = llm.bind_tools(tools)

    conversation = [
        {"role": "system", "content": "You are AI assistant"},
        {"role": "user", "content": "What is a price of MSFT?"},
    ]

    # call model
    res = llm_with_tools.invoke(conversation)
    print("---- Response ----")
    print(res.content)
    print(res.tool_calls)


if __name__ == "__main__":
    asyncio.run(main())
