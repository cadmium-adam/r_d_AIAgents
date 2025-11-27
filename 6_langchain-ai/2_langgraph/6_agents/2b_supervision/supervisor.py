from langchain_openai import ChatOpenAI
from langchain.tools import tool


# Tools = possible hand-offs
@tool("transfer_to_researcher", description="Ask the researcher for help.")
def transfer_to_researcher():
    """Transfer the task to the researcher."""
    return {"next": "researcher"}


@tool("transfer_to_coder", description="Ask the coder for help.")
def transfer_to_coder():
    """Transfer the task to the coder."""
    return {"next": "coder"}


tools = [transfer_to_researcher, transfer_to_coder]


# model
llm = ChatOpenAI(model="gpt-5-nano", temperature=0)

llm_with_tools = llm.bind_tools(tools, tool_choice="required")


# Prompt
members = ["researcher", "coder"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

conversation = [
    {"role": "system", "content": system_prompt.format(members=", ".join(members))},
    {
        "role": "user",
        "content": "Given the conversation above, who should act next?"
        " Or should we FINISH? Select one of: {members}".format(
            members=", ".join(members)
        ),
    },
]
