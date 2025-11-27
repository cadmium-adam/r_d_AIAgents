import os
from dotenv import load_dotenv, find_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

_ = load_dotenv(find_dotenv())  # read local .env file

# ----------------------
# Hugging face Endpoint
# ----------------------

# model
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFaceEndpoint(
    repo_id=repo_id,
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)

# Chat
chat = ChatHuggingFace(llm=llm, verbose=True)

messages = [
    ("system", "You are a helpful AI Assistant."),
    ("human", "What would be a good company name for a company that makes colorful socks?"),
]

response = chat.invoke(messages)
print(response.content)

