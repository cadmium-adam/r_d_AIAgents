import json
import asyncio
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.stdio import stdio_server

from tools.get_stock_price import get_stock_price
from tools.get_dividend_date import get_dividend_date

server = Server("mcp-finance")

# ----------------------------------
# ----------------------------------
# Tools
# ----------------------------------
# ----------------------------------


async def run_server():

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="get_stock_price",
                description="Get the current stock price.",
                inputSchema={
                    "type": "object",
                    "required": ["ticker"],
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g., AAPL, GOOG)",
                        }
                    },
                },
            ),
            types.Tool(
                name="get_dividend_date",
                description="Get the next dividend date of a stock.",
                inputSchema={
                    "type": "object",
                    "required": ["ticker"],
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "The stock ticker symbol (e.g., AAPL, GOOG)",
                        }
                    },
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

        print("CALL TOOL")
        print(name)
        print(arguments)

        result = None
        if name == "get_stock_price":
            result = get_stock_price(arguments["ticker"])
        elif name == "get_dividend_date":
            result = get_dividend_date(arguments["ticker"])

        print("Result:")
        print(result)

        result_json = json.dumps(result)

        return [types.TextContent(type="text", text=result_json)]

    # run the server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    asyncio.run(run_server())
