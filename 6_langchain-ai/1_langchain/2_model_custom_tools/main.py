from langchain_openai import ChatOpenAI
from langchain.tools import tool
import yfinance as yf
from dotenv import load_dotenv

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


tools = [get_stock_price, get_dividend_date]


# model
llm = ChatOpenAI(model="gpt-5-nano")

llm_with_tools = llm.bind_tools(tools)


conversation = [
    {"role": "system", "content": "You are AI assistant"},
    {"role": "user", "content": "What is a price of MSFT?"},
]

# call model
res = llm.invoke(conversation)
print("---- Response ----")
print(res.content)
