import operator
from datetime import datetime
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from visualizer import visualize
from langgraph.graph import START, END

# ---------------------------
# Define the graph
# ---------------------------

# State
class State(TypedDict):
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

# Add edges
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", "d")
builder.add_edge("d", END)

# or set entry and finish points
# builder.set_entry_point("a")
# builder.set_finish_point("b")

# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------
initial_state = {"data": []}
result = graph.invoke(initial_state)
print(result)
