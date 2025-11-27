from typing import Annotated, Any, Literal, Sequence
from datetime import datetime
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from visualizer import visualize
import operator
from langgraph.graph import START, END


# ---------------------------
# Define the graph
# ---------------------------


# State
class State(TypedDict):
    question: str
    # with aggregation
    data: Annotated[list, operator.add]
    # without aggregation
    # data: List[Any]


# Nodes
def node_a(state: State):
    return {"data": [f"A - {datetime.now().strftime("%S.%f")}"]}

def node_b(state: State):
    return {"data": [f"B - {datetime.now().strftime("%S.%f")}"]}

def node_c(state: State):
    return {"data": [f"C - {datetime.now().strftime("%S.%f")}"]}

def node_d(state: State):
    return {"data": [f"D - {datetime.now().strftime("%S.%f")}"]}


# Build the graph
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_node("d", node_d)


def route_b_or_c(state: State) -> Literal["b", "c"]:
    if state["question"].startswith("What is"):
        return ["b"]
    else:
        return ["c"]


# Add edges
builder.add_edge(START, "a")
builder.add_conditional_edges("a", route_b_or_c)
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

# or set entry and finish points
# builder.set_entry_point("a")
# builder.set_finish_point("d")


# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------
result = graph.invoke({"question": "Who is car?", "aggregate": []})
print("Result:")
print(result)
