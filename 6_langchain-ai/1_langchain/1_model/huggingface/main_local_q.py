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
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True,
)

# model
repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
llm = HuggingFacePipeline.from_model_id(
    model_id=repo_id,
    task="text-generation",
    pipeline_kwargs={"max_new_tokens": 100},
    model_kwargs={"quantization_config": quantization_config},
)

# LLM
res = llm.invoke("What is a good name for a company that makes colorful socks?")
print("---- Response ----")
print(res)
