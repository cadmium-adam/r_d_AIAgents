from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

tavily_tool = TavilySearchResults(max_results=5)

# Note: PythonREPL removed - incompatible with langgraph 1.0.2
# If you need a Python REPL tool, consider using E2B Code Interpreter or similar sandbox

tools = [tavily_tool]
