from typing import Annotated, Any, Literal, Sequence
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
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
    counter: int
    # with aggregation
    data: Annotated[list, operator.add]
    # without aggregation
    # data: List[Any]


# Test node
def node_a(state: State):
    return {"data": [f"A - {datetime.now().strftime("%S.%f")}"]}

def node_b(state: State):
    return {"data": [f"B - {datetime.now().strftime("%S.%f")}"]}

def node_c(state: State):
    return {
        "data": [f"C - {datetime.now().strftime("%S.%f")}"],
        "counter": state["counter"] + 1 # <-------------------------------------- increment counter
        }

def node_d(state: State):
    return {"data": [f"D - {datetime.now().strftime("%S.%f")}"]}


# Build the graph
builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_node("c", node_c)
builder.add_node("d", node_d)

def shouldContinue(state: State) -> Literal["b", "d"]:
    if state["counter"] < 3:
        return ["b"]
    else:
        return ["d"]


builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_conditional_edges("c", shouldContinue)
builder.add_edge("d", END)


# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------
initial_state = {"question": "What is car?", "counter": 0, "data": []}
result = graph.invoke(initial_state)
print("Result:")
print(result)
