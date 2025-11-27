"""
Agent as Tool - Tool Calling Pattern Demonstration

This example shows how to use one agent (controller) that treats other agents as tools.
The controller orchestrates when and how to invoke specialized subagents.

This example uses Tavily via MCP (Model Context Protocol) for web search.
"""

import asyncio
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

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

    # Get tools from the MCP server
    tools = await client.get_tools()
    return tools, client


# ============================================================================
# SUBAGENT 1: Research Agent
# ============================================================================


async def create_research_agent(mcp_tools):
    """Create a research agent that can search the web using Tavily MCP."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    research_agent = create_agent(
        llm,
        tools=mcp_tools,  # Use Tavily MCP tools
        system_prompt="""You are a research specialist. Your job is to find accurate,
        up-to-date information on the web. When you receive a query:
        1. Use the tavily_search tool to find relevant information
        2. Synthesize the findings into a clear, concise answer
        3. Include the key facts and sources when relevant

        IMPORTANT: The controller agent and user only see your final message,
        so make sure to include all relevant information in your response.""",
    )
    return research_agent


# ============================================================================
# SUBAGENT 2: Calculator Agent
# ============================================================================


@tool(
    "calculate",
    description="Perform a mathematical calculation. Input should be a valid Python mathematical expression.",
)
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A valid Python mathematical expression (e.g., "2 + 2", "10 * 5 - 3")

    Returns:
        The result of the calculation as a string
    """
    try:
        # Using eval with limited scope for safety
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


async def create_calculator_agent():
    """Create a calculator agent that can perform mathematical operations."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    calculator_agent = create_agent(
        llm,
        tools=[calculate],
        system_prompt="""You are a mathematical calculation specialist.
        When you receive a math problem:
        1. Parse the problem to understand what calculation is needed
        2. Use the calculate tool to perform the computation
        3. Return a clear answer with the result

        IMPORTANT: The controller agent and user only see your final message,
        so make sure to include the complete answer in your response.""",
    )
    return calculator_agent


# ============================================================================
# TOOL WRAPPERS FOR SUBAGENTS
# ============================================================================


# Global variables to store agents (will be initialized in main)
research_agent = None
calculator_agent = None


@tool(
    "research_assistant",
    description="Use this tool when you need to search for current information on the web, "
    "look up facts, find recent news, or research any topic. "
    "Input should be a clear question or search query.",
)
async def call_research_agent(query: str) -> str:
    """
    Invoke the research agent to search for information.

    Args:
        query: The research question or search query

    Returns:
        The research agent's findings
    """
    result = await research_agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    return result["messages"][-1].content


@tool(
    "math_assistant",
    description="Use this tool when you need to perform mathematical calculations, "
    "solve equations, or compute numerical results. "
    "Input should be a clear description of the math problem.",
)
async def call_calculator_agent(query: str) -> str:
    """
    Invoke the calculator agent to perform calculations.

    Args:
        query: The mathematical problem or calculation request

    Returns:
        The calculator agent's result
    """
    result = await calculator_agent.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    return result["messages"][-1].content


# ============================================================================
# CONTROLLER AGENT
# ============================================================================


async def create_controller_agent():
    """Create the controller agent that can invoke subagents as tools."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    controller = create_agent(
        llm,
        tools=[call_research_agent, call_calculator_agent],
        system_prompt="""You are an intelligent assistant that coordinates specialized agents
        to help users. You have access to:

        1. research_assistant: For web searches and finding current information
        2. math_assistant: For mathematical calculations

        Your job is to:
        - Understand the user's request
        - Decide which specialized agent(s) to invoke
        - Use the results to provide a helpful response
        - Combine information from multiple agents if needed

        Be concise and accurate in your responses.""",
    )
    return controller


# ============================================================================
# DEMONSTRATION
# ============================================================================


async def demo_simple_calculation():
    """Example 1: Simple calculation using the math assistant"""
    print("=" * 80)
    print("EXAMPLE 1: Simple Calculation")
    print("=" * 80)

    controller = await create_controller_agent()

    query = "What is 156 multiplied by 47?"
    print(f"\nUser: {query}\n")

    result = await controller.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    print(f"Controller: {result['messages'][-1].content}\n")


async def demo_research_task():
    """Example 2: Research task using the research assistant"""
    print("=" * 80)
    print("EXAMPLE 2: Research Task")
    print("=" * 80)

    controller = await create_controller_agent()

    query = "What are the latest developments in AI agents for 2025?"
    print(f"\nUser: {query}\n")

    result = await controller.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    print(f"Controller: {result['messages'][-1].content}\n")


async def demo_combined_task():
    """Example 3: Task requiring both research and calculation"""
    print("=" * 80)
    print("EXAMPLE 3: Combined Task")
    print("=" * 80)

    controller = await create_controller_agent()

    query = "Find the current price of Bitcoin and calculate what 5 bitcoins would be worth."
    print(f"\nUser: {query}\n")

    result = await controller.ainvoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    print(f"Controller: {result['messages'][-1].content}\n")


async def main():
    """Main async function to run all demonstrations."""
    global research_agent, calculator_agent

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "AGENT AS TOOL - TOOL CALLING PATTERN" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    # Load MCP tools and create agents
    print("Initializing MCP connection to Tavily...")
    mcp_tools, mcp_client = await get_mcp_tools()
    print(f"Loaded {len(mcp_tools)} tools from Tavily MCP\n")

    # Initialize subagents
    research_agent = await create_research_agent(mcp_tools)
    calculator_agent = await create_calculator_agent()

    # Run demonstrations
    # Note: MultiServerMCPClient manages sessions automatically, no cleanup needed
    await demo_simple_calculation()
    await demo_research_task()
    await demo_combined_task()

    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
