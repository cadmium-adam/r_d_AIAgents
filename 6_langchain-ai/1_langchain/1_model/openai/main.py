from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# model
llm = ChatOpenAI(model="gpt-5-nano")

conversation = [
    {"role": "system", "content": "You are AI assistant"},
    {"role": "user", "content": "Hi, I am Lukas"},
    {"role": "assistant", "content": "Hello Lukas, how can I assist you today?"},
    {
        "role": "user",
        "content": "What is a good name for a company that makes colorful socks?",
    },
]

# # call model
# res = llm.invoke(conversation)
# print("---- Response ----")
# print(res.content)

# streaming response
print("---- Streaming Response ----")
for chunk in llm.stream(conversation):
    print(chunk.text, end="", flush=True)
