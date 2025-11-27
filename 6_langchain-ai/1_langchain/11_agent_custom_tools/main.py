from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()


@tool(
    "get_stock_price",
    description="Get the current stock price for a given ticker symbol.",
)
def get_stock_price(ticker: str) -> dict:
    """Retrieve the current stock price for a given ticker symbol.

    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL', 'GOOGL').

    Returns:
        A dictionary containing:
            - 'ticker': The provided ticker symbol.
            - 'current_price': The current stock price, or None if unavailable.
    """
    ticker_info = yf.Ticker(ticker).info
    current_price = ticker_info.get("currentPrice")
    return {"ticker": ticker, "current_price": current_price}


@tool(
    "get_dividend_date",
    description="Get the next dividend date for a given ticker symbol.",
)
def get_dividend_date(ticker: str) -> dict:
    """Retrieve the next dividend date for a given ticker symbol.

    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL', 'GOOGL').

    Returns:
        A dictionary containing:
            - 'ticker': The provided ticker symbol.
            - 'dividend_date': The date of the next dividend payment (as a UNIX timestamp), or None if unavailable.
    """
    ticker_info = yf.Ticker(ticker).info
    dividend_date = ticker_info.get("dividendDate")
    return {"ticker": ticker, "dividend_date": dividend_date}


# model
llm = ChatOpenAI(model="gpt-5-mini")

# agent
agent = create_agent(
    llm,
    tools=[get_stock_price, get_dividend_date],
    system_prompt="You are a helpful assistant. Be concise and accurate.",
)

# conversation = {
#     "messages": [
#         {"role": "user", "content": "What is a price of MSFT?"},
#     ]
# }


conversation = {"messages": [{"role": "user", "content": "What is a price of MSFT?"}]}

# call model
res = agent.invoke(conversation)
print("---- Response ----")
print(res["messages"][-1].content)
