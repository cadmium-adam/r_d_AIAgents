from typing import Literal
from langgraph.graph import StateGraph, START
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing_extensions import TypedDict


class SwarmState(AgentState):
    """State schema for the swarm system with active agent tracking."""

    active_agent: Literal["researcher", "coder", "summarizer"] | None


def create_swarm_graph(
    agents: dict,
    default_active_agent: str = "researcher",
) -> StateGraph:
    """
    Create a pure LangGraph StateGraph that implements swarm behavior.

    Args:
        agents: Dictionary mapping agent names to agent graphs
        default_active_agent: The agent to start with

    Returns:
        Uncompiled StateGraph
    """
    # Create the state graph
    builder = StateGraph(SwarmState)

    # Add router from START to active agent
    def route_to_active_agent(state: SwarmState) -> str:
        """Route to the active agent or default if none set."""
        return state.get("active_agent") or default_active_agent

    # Create path map for routing
    agent_names = list(agents.keys())
    path_map = {name: name for name in agent_names}

    # Add conditional edge from START
    builder.add_conditional_edges(
        START,
        route_to_active_agent,
        path_map=path_map,
    )

    # Add each agent as a node
    for agent_name, agent_graph in agents.items():
        builder.add_node(agent_name, agent_graph)

    return builder
