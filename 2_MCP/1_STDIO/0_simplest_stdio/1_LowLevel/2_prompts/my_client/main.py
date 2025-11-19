import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_script = "../my_server/main.py"  # Path to the MCP server script

    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as stdio_transport:
        async with ClientSession(*stdio_transport) as session:
            # Initialize
            result = await session.initialize()
            print("\n=== Initialize ===")
            print(result)

            # Ping
            ping_result = await session.send_ping()
            print("\n=== Ping ===")
            print(ping_result)

            # List prompts
            print("\n=== Available Prompts ===")
            prompts_list_response = await session.list_prompts()
            for prompt in prompts_list_response.prompts:
                print(f"- {prompt.name}: {prompt.description}")

            # Get 'stock-summary' prompt
            print("\n=== Get Prompt: stock-summary ===")
            stock_prompt = await session.get_prompt(
                "stock-summary",
                arguments={"ticker": "AAPL", "days": "5"}
            )
            for msg in stock_prompt.messages:
                print(f"{msg.role}: {msg.content.text}")

            # Get 'investment-evaluation' prompt
            print("\n=== Get Prompt: investment-evaluation ===")
            invest_prompt = await session.get_prompt(
                "investment-evaluation",
                arguments={
                    "company_name": "Tesla",
                    "sector": "Automotive",
                    "risk_tolerance": "high"
                }
            )
            for msg in invest_prompt.messages:
                print(f"{msg.role}: {msg.content.text}")


if __name__ == "__main__":
    asyncio.run(main())
