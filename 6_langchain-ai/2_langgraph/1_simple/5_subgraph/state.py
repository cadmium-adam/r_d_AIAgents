from typing import TypedDict

# State
class State(TypedDict):
    question: str
    query: str
    search: str
    docs: str
    answer: str
    summarization: str
