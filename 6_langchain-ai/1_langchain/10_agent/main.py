from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv

load_dotenv()

# model
llm = ChatOpenAI(model="gpt-5-nano")

# agent
agent = create_agent(
    llm, tools=[], system_prompt="You are a helpful assistant. Be concise and accurate."
)

conversation = {
    "messages": [
        {"role": "user", "content": "What is a price of MSFT?"},
    ]
}

# call model
res = agent.invoke(conversation)
print("---- Response ----")
print(res["messages"][-1].content)
