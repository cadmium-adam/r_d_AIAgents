from dotenv import load_dotenv, find_dotenv
from langgraph.graph import StateGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import START, END
import json
from graph import (
    MyState,
    ResearcherNode,
    CoderNode,
    SupervisorNode,
    supervisor_router,
)
from devtools import pprint
from visualizer import visualize

_ = load_dotenv(find_dotenv())  # read local .env file


async def main():

    # ---------------------------
    # Define the graph
    # ---------------------------
    workflow = StateGraph(MyState)

    workflow.add_node("researcher", ResearcherNode)
    workflow.add_node("coder", CoderNode)
    workflow.add_node("supervisor", SupervisorNode)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        supervisor_router,
        {"researcher": "researcher", "coder": "coder", "__end__": END},
    )
    workflow.add_edge("coder", "supervisor")
    workflow.add_edge("researcher", "supervisor")

    # Graph object
    graph = workflow.compile()

    # Visualize the graph
    visualize(graph, "graph.png")

    # ---------------------------
    # Run the graph
    # ---------------------------

    conversation = {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Give me investment advice for MSFT stock and save it into a file,"
                    "and then draw a graph of the close price and save it into a file."
                ),
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
                subgraph_name = (
                    namespace[-1].split(":")[0]
                    if ":" in namespace[-1]
                    else namespace[-1]
                )
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
                                        server_name, tool_name = parse_mcp_tool_name(
                                            tc["name"]
                                        )

                                        if server_name:
                                            print(f"   └─ [{server_name}] {tool_name}")
                                        else:
                                            print(f"   └─ {tool_name}")

                                        print(f"      {tc['args']}")

                            elif isinstance(message, ToolMessage):
                                tool_name = getattr(message, "name", "unknown")
                                server_name, actual_tool_name = parse_mcp_tool_name(
                                    tool_name
                                )

                                if server_name:
                                    print(
                                        f"✅ [{server_name}] {actual_tool_name} Result:"
                                    )
                                else:
                                    print(f"✅ {actual_tool_name} Result:")

                                result = str(message.content)[:300]
                                print(
                                    f"   {result}{'...' if len(str(message.content)) > 300 else ''}"
                                )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
