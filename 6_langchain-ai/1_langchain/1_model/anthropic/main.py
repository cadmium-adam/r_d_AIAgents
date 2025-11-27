from langchain_anthropic import ChatAnthropic

# from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# model
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

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
