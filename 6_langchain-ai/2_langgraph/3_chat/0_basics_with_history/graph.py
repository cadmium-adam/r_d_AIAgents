from typing import Annotated
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from visualizer import visualize
from langgraph.graph import START, END


_ = load_dotenv(find_dotenv())  # read local .env file


# Model
llm = ChatOpenAI(model="gpt-4.1-nano")


# ---------------------------
# Define the graph
# ---------------------------


# State
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


# Node 1
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

# Entry and finish points
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)


# Graph object
my_graph = graph_builder.compile()

# Visualize the graph
visualize(my_graph, "graph.png")

