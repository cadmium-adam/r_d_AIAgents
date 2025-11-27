from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from visualizer import visualize
from langgraph.graph import START, END
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

_ = load_dotenv(find_dotenv())  # read local .env file


# Model
llm = ChatOpenAI(model="gpt-4o-mini")


# load DB from disk
embeddings = OllamaEmbeddings(model="mistral")
vector_store = Chroma(
    collection_name="my_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_db",  # Where to save data locally, remove if not necessary
)


# ---------------------------
# Define the graph
# ---------------------------

# State
class State(TypedDict):
    question: str
    query: str
    docs: str
    answer: str


# Prepare query node
def PrepareQueryNode(state: State):
    print("PrepareQueryNode")
    print(state)

    messages = [
        {"role": "system", "content": "Improve the user query, so it can be used for a query in vector DB."},
        {"role": "user", "content": f"User question: {state['question']}"},
    ]
    response = llm.invoke(messages)
    return {"query": response.content}

# DB Call node
def GetDataFromDBNode(state: State):
    print("GetDataFromDBNode")
    print(state)

    docs = vector_store.similarity_search(state["query"])

    return {"docs": docs}

# Format answer node (LLM call)
def FormatAnswerNode(state: State):
    print("FormatAnswerNode")
    print(state)

    messages = [
        {"role": "system", "content": "You are an AI assistant focused on formatting the clear result answer from question and context!"},
        {"role": "user", "content": f"""
                     Question:
                     ===
                     {state['question']}
                     ===

                     Context:
                     ===
                     {state['docs']}
                     ===
                     """},
    ]
    response = llm.invoke(messages)
    return {"answer": response}

# Log node 
def LogNode(state: State):
    print("LogNode")
    print(state)
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("prepareQuery", PrepareQueryNode)
builder.add_node("calldb", GetDataFromDBNode)
builder.add_node("formatAnswer", FormatAnswerNode)
builder.add_node("log", LogNode)

builder.add_edge(START, "prepareQuery")
builder.add_edge("prepareQuery", "calldb")
builder.add_edge("calldb", "formatAnswer")
builder.add_edge("formatAnswer", "log")
builder.add_edge("log", END)

# Graph object
graph = builder.compile()

# Visualize the graph
visualize(graph, "graph.png")


# ---------------------------
# Run the graph
# ---------------------------
question = "space"
initial_state = { "question": "What are use cases for Autogen? Does it supports multi-agent scenarios?"}
result = graph.invoke(initial_state)
print("--------- Result ---------")
print(result["answer"].content)