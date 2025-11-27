from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from visualizer import visualize
from handoff import transfer_to_coder, transfer_to_researcher

# model
llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

summarizer_agent = create_react_agent(
    model=llm,
    tools=[transfer_to_coder, transfer_to_researcher],
    prompt=(
        "You are a summarizer, you summarize the output to understandable output for user."
    ),
)

# Visualize the agent graph
visualize(summarizer_agent, "summarizer_agent.png")
