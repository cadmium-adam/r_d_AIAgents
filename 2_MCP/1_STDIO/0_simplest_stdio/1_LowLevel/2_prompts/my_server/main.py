import json
import asyncio
from mcp.server.lowlevel import Server
import mcp.types as types 
from mcp.server.stdio import stdio_server

server = Server("mcp-finance")

# ----------------------------------
# Tools (Prompts)
# ----------------------------------

async def run_server():

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        return [
            types.Prompt(
                name="stock-summary",
                description="Generate a brief summary of a specific stock's recent performance.",
                arguments=[
                    types.PromptArgument(name="ticker", description="Stock ticker symbol (e.g., AAPL, TSLA)", required=True),
                    types.PromptArgument(name="days", description="Number of past days to include in the summary", required=True),
                ],
            ),
            types.Prompt(
                name="investment-evaluation",
                description="Evaluate an investment opportunity based on user-provided details.",
                arguments=[
                    types.PromptArgument(name="company_name", description="Name of the company", required=True),
                    types.PromptArgument(name="sector", description="Sector the company operates in", required=True),
                    types.PromptArgument(name="risk_tolerance", description="User's risk tolerance (low, medium, high)", required=True),
                ],
            )
        ]

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:

        if name == "stock-summary":
            ticker = arguments.get("ticker", "UNKNOWN")
            days = arguments.get("days", "7")
            return types.GetPromptResult(
                description="Prompt to summarize stock performance",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Give me a summary of {ticker} stock performance over the past {days} days."
                        ),
                    )
                ],
            )

        elif name == "investment-evaluation":
            company = arguments.get("company_name", "Unnamed Company")
            sector = arguments.get("sector", "Unknown")
            risk = arguments.get("risk_tolerance", "medium")
            return types.GetPromptResult(
                description="Prompt to evaluate an investment opportunity",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=(
                                f"Evaluate the investment opportunity in {company}, operating in the {sector} sector. "
                                f"The investor has a {risk} risk tolerance."
                            )
                        ),
                    )
                ],
            )

        else:
            raise ValueError(f"Unknown prompt: {name}")

    # ----------------------------------
    # Run the server
    # ----------------------------------
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    asyncio.run(run_server())
