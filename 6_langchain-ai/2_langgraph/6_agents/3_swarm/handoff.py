from typing import Annotated
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.types import Command


@tool
def transfer_to_coder(
    state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Transfer control to the coder agent."""
    tool_message = ToolMessage(
        content="Transferred to coder",
        tool_call_id=tool_call_id,
    )
    return Command(
        goto="coder",
        graph=Command.PARENT,
        update={
            "messages": [*state["messages"], tool_message],
            "active_agent": "coder",
        },
    )


@tool
def transfer_to_researcher(
    state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Transfer control to the researcher agent."""
    tool_message = ToolMessage(
        content="Transferred to researcher",
        tool_call_id=tool_call_id,
    )
    return Command(
        goto="researcher",
        graph=Command.PARENT,
        update={
            "messages": [*state["messages"], tool_message],
            "active_agent": "researcher",
        },
    )


@tool
def transfer_to_summarizer(
    state: Annotated[AgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Transfer control to the summarizer agent."""
    tool_message = ToolMessage(
        content="Transferred to summarizer",
        tool_call_id=tool_call_id,
    )
    return Command(
        goto="summarizer",
        graph=Command.PARENT,
        update={
            "messages": [*state["messages"], tool_message],
            "active_agent": "summarizer",
        },
    )
