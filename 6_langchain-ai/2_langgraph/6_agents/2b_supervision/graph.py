import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from agent_researcher import create_researcher_agent
from agent_coder import create_coder_agent
import json
import io
from PIL import Image
from devtools import pprint
from supervisor import conversation, llm_with_tools


# ----------------------------------
# State
# ----------------------------------
class MyState(TypedDict):
    messages: Annotated[list, operator.add]
    # The 'next' field indicates where to route to next
    next: str


# ----------------------------------
# Node 0 = Supervisor
# ----------------------------------
def SupervisorNode(state: MyState):
    """Supervisor node."""
    print("----- Supervisor Node -----")
    print("state:")
    pprint(state)

    # Invoke the node
    all_messages = conversation + state["messages"]
    result = llm_with_tools.invoke(all_messages)
    pprint(result)

    # Parse the tool call to determine next agent
    next_agent = "__end__"
    if result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_name = tool_call["name"]

        if tool_name == "transfer_to_researcher":
            next_agent = "researcher"
        elif tool_name == "transfer_to_coder":
            next_agent = "coder"
        elif tool_name == "finish":
            next_agent = "__end__"

    return {
        "next": next_agent,  # Return string, not AIMessage
    }


# ----------------------------------
# Node 1 = Researcher
# ----------------------------------
async def ResearcherNode(state: MyState):
    """Researcher agent."""
    name = "researcher"

    print("----- Researcher Node -----")

    # Invoke the agent
    researcher_agent = await create_researcher_agent()
    result = await researcher_agent.ainvoke(state)
    # pprint(result)

    last_message = result["messages"][-1]
    print("Last message:", last_message)

    return {
        "messages": [last_message],
    }


# ----------------------------------
# Node 2 = Coder
# ----------------------------------
async def CoderNode(state: MyState):
    """Coder agent."""
    name = "coder"

    print("----- Coder Node -----")

    # Invoke the agent
    coder_agent = await create_coder_agent()
    result = await coder_agent.ainvoke(state)
    # pprint(result)

    last_message = result["messages"][-1]
    print("Last message:", last_message)

    # result = AIMessage(content=result["output"], name=name)
    return {
        "messages": [last_message],
    }


# ----------------------------------
# router edge
# ----------------------------------
def supervisor_router(state) -> Literal["coder", "researcher", "__end__"]:

    print("----- Supervisor Router 1 -----")
    print(state)

    next = state["next"]

    print("----- Supervisor Router 2 -----")
    pprint(next)

    return next
