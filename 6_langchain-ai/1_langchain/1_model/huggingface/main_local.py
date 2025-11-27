import os
from huggingface_hub import login
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from transformers import BitsAndBytesConfig
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# ----------------------
# Hugging face Pipeline
# ----------------------
# model
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFacePipeline.from_model_id(
    model_id=repo_id,
    task="text-generation",
    pipeline_kwargs={"max_new_tokens": 100},
)

# LLM
res = llm.invoke("What is a good name for a company that makes colorful socks?")
print("---- Response ----")
print(res)
