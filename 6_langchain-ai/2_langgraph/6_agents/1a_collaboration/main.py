from typing_extensions import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Literal, TypedDict
from visualizer import visualize
from langgraph.graph.message import add_messages
from typing import Annotated, Any, List
import os
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from visualizer import visualize
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import START, END
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage

load_dotenv()

# Model
llm = ChatOpenAI(model="gpt-5-nano")


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
    


async def main():

    research_tools, _ = await get_research_mcp_tools()
    coder_tools, _ = await get_coder_mcp_tools()

    # Agent
    coder_agent = create_agent(
        model=llm,
        tools=coder_tools,
        system_prompt="You are the most amazing software developer in the world. If you or any of the other assistants have the final answer or deliverable, prefix your response with [[[[FINAL ANSWER]]]] so the team knows to stop.",
    )
    researcher_agent = create_agent(
        model=llm,
        tools=research_tools,
        system_prompt="You are the most amazing researcher in the world. If you or any of the other assistants have the final answer or deliverable, prefix your response with [[[[FINAL ANSWER]]]] so the team knows to stop.",
    )

    # GRAPH

    # State
    class State(TypedDict):
        messages: Annotated[list, add_messages]


    # Build the graph
    builder = StateGraph(State)
    builder.add_node("coder_agent", coder_agent)
    builder.add_node("researcher_agent", researcher_agent)


    def decide_next_agent_1(state: State) -> Literal["researcher_agent", "__end__"]:
        last_message = state["messages"][-1]
        if (
            isinstance(last_message, AIMessage)
            and "[[[[FINAL ANSWER]]]]" in last_message.content
        ):
            return "__end__"
        return "researcher_agent"


    def decide_next_agent_2(state: State) -> Literal["coder_agent", "__end__"]:
        last_message = state["messages"][-1]
        if (
            isinstance(last_message, AIMessage)
            and "[[[[FINAL ANSWER]]]]" in last_message.content
        ):
            return "__end__"
        return "coder_agent"


    builder.add_edge(START, "researcher_agent")
    builder.add_conditional_edges("researcher_agent", decide_next_agent_2)
    builder.add_conditional_edges("coder_agent", decide_next_agent_1)

    # Graph object
    graph = builder.compile()

    # Visualize the graph
    visualize(graph, "graph.png")


    # ---------------------------
    # Run the graph
    # ---------------------------

    # conversation = {
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": "Give me investment advice for MSFT stock and save it into a file, and then draw a graph of the close price and save it into a file."
    #             }
    #         ],
    #     }
    
    conversation = {
            "messages": [
                {
                    "role": "user",
                    "content": "Find for me a recent research paper on arxiv about reinforcement learning, summarize its key findings, and write a Python script that implements a basic version of the main algorithm discussed in the paper."
                }
            ],
        }

    def parse_mcp_tool_name(tool_name: str) -> tuple[str | None, str]:
        """
        Parse MCP tool name to extract server name and actual tool name.

        Args:
            tool_name: Full tool name (e.g., "mcp__tavily__search" or "regular_tool")

        Returns:
            Tuple of (server_name, actual_tool_name).
            server_name is None if not an MCP tool.
        """
        if tool_name.startswith("mcp__"):
            parts = tool_name.split("__")
            if len(parts) >= 3:
                server_name = parts[1]
                actual_tool_name = "__".join(parts[2:])
                return server_name, actual_tool_name
        return None, tool_name


    async for chunk in graph.astream(
        conversation,
        stream_mode="updates",
        subgraphs=True,
    ):
        if isinstance(chunk, tuple) and len(chunk) == 2:
            namespace, data = chunk

            if namespace:
                subgraph_name = namespace[-1].split(':')[0] if ':' in namespace[-1] else namespace[-1]
            else:
                subgraph_name = "main"

            if isinstance(data, dict):
                for node_name, node_data in data.items():
                    print(f"\n{'='*60}")
                    print(f"🔷 [{subgraph_name}] Node: {node_name}")
                    print(f"{'='*60}")

                    if "messages" in node_data:
                        messages = node_data["messages"]
                        if not isinstance(messages, list):
                            messages = [messages]

                        for message in messages:
                            print(f"\n📌 {type(message).__name__}")

                            if isinstance(message, AIMessage):
                                if message.content:
                                    print(f"💬 {message.content[:500]}")

                                if message.tool_calls:
                                    print("\n🔧 Tool Calls:")
                                    for tc in message.tool_calls:
                                        server_name, tool_name = parse_mcp_tool_name(tc['name'])

                                        if server_name:
                                            print(f"   └─ [{server_name}] {tool_name}")
                                        else:
                                            print(f"   └─ {tool_name}")

                                        print(f"      {tc['args']}")

                            elif isinstance(message, ToolMessage):
                                tool_name = getattr(message, 'name', 'unknown')
                                server_name, actual_tool_name = parse_mcp_tool_name(tool_name)

                                if server_name:
                                    print(f"✅ [{server_name}] {actual_tool_name} Result:")
                                else:
                                    print(f"✅ {actual_tool_name} Result:")

                                result = str(message.content)[:300]
                                print(f"   {result}{'...' if len(str(message.content)) > 300 else ''}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())