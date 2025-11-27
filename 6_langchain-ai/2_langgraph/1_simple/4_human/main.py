from typing import Literal
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from visualizer import visualize
from langgraph.graph import START, END

_ = load_dotenv(find_dotenv())  # read local .env file

# Model
llm = ChatOpenAI(model="gpt-4o-mini")

# ---------------------------
# Define the graph
# ---------------------------

# State
class State(TypedDict):
    theme: str
    jokeText: str
    storyText: str


# Joke node
def JokeNode(state: State):
    messages = [
        {"role": "system", "content": "You are a hilarious person!"},
        {"role": "user", "content": f"Generate a joke on theme: {state['theme']}"},
    ]
    response = llm.invoke(messages)
    return {"jokeText": response}

# Story node
def StoryNode(state: State):
    messages = [
        {"role": "system", "content": "You are a storyteller!"},
        {"role": "user", "content": f"Generate a story for this joke: {state['jokeText']}"},
    ]
    response = llm.invoke(messages)
    return {"storyText": response}

def HumanNode(state: State):
    pass


def askHuman(state: State) -> Literal["joke", "story"]:
    print("Here is a joke, do you like it?")
    print("--------------------------------")
    print(state["jokeText"].content)
    print("--------------------------------")
    user_input = input("Answer: ")
    if user_input == "yes":
        return ["story"]
    else:
        return ["joke"]

# Build the graph
builder = StateGraph(State)
builder.add_node("joke", JokeNode)
builder.add_node("human", HumanNode)
builder.add_node("story", StoryNode)

builder.add_edge(START, "joke")
builder.add_edge("joke", "human")
builder.add_conditional_edges("human", askHuman)
builder.add_edge("story", END)


# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------
theme = "space"
initial_state = { "theme": theme }
result = graph.invoke(initial_state)
print(result)