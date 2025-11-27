from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# model
llm = ChatOllama(
    model="mistral:latest",
    temperature=0,
)


conversation = [
    {"role": "system", "content": "You are AI assistant"},
    {"role": "user", "content": "Hi, I am Lukas"},
    {"role": "assistant", "content": "Hello Lukas, how can I assist you today?"},
    {
        "role": "user",
        "content": "What is a good name for a company that makes colorful socks?",
    },
]

# call model
res = llm.invoke(conversation)
print("---- Response ----")
print(res.content)
