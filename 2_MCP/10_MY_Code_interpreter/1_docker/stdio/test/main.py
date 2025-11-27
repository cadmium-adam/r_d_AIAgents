# test_mcp_python_executor.py
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def test_simple_python():
    """Test simple Python code execution without dependencies."""

    server_params = StdioServerParameters(
        command="docker",
        args=["run", "-i", "--rm", "mcp-python-executor"],
        env=None,
    )

    print("=" * 60)
    print("TEST 1: Simple Python Script")
    print("=" * 60)

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:

                # Initialize
                await session.initialize()
                print("✓ Connected to MCP server")

                # Test 1: Basic print and arithmetic
                print("\n1. Basic print and arithmetic:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
print("Hello from MCP!")
x = 10
y = 20
print(f"The sum of {x} and {y} is {x + y}")
"""
                    },
                )
                print_result(result)

                # Test 2: Functions and loops
                print("\n2. Functions and loops:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

print("First 10 Fibonacci numbers:")
print(fibonacci(10))

# Test list comprehension
squares = [x**2 for x in range(1, 6)]
print(f"Squares of 1-5: {squares}")
"""
                    },
                )
                print_result(result)

                # Test 3: Working with built-in modules
                print("\n3. Built-in modules (datetime, random, math):")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
import datetime
import random
import math
import json
import os

# DateTime operations
now = datetime.datetime.now()
print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Random numbers
random.seed(42)
numbers = [random.randint(1, 100) for _ in range(5)]
print(f"Random numbers: {numbers}")

# Math operations
print(f"Square root of 144: {math.sqrt(144)}")
print(f"Pi value: {math.pi:.6f}")

# JSON operations
data = {"name": "test", "value": 123}
json_str = json.dumps(data, indent=2)
print(f"JSON data:\\n{json_str}")

# Environment info
print(f"Python executable: {os.sys.executable}")
"""
                    },
                )
                print_result(result)

                # Test 4: Error handling
                print("\n4. Error handling test:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")

# This should produce an error
print("This line executes")
undefined_variable  # This will cause an error
print("This line won't execute")
"""
                    },
                )
                print_result(result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


async def test_with_dependencies():
    """Test Python code execution with external dependencies."""

    server_params = StdioServerParameters(
        command="docker",
        args=["run", "-i", "--rm", "mcp-python-executor"],
        env=None,
    )

    print("\n" + "=" * 60)
    print("TEST 2: Python Scripts with Dependencies")
    print("=" * 60)

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:

                # Initialize
                await session.initialize()
                print("✓ Connected to MCP server")

                # Test 1: Install and use requests
                print("\n1. Testing with 'requests' library:")
                print("   Installing requests...")
                result = await session.call_tool(
                    name="install_dependencies", arguments={"packages": ["requests"]}
                )
                print_result(result)

                print("   Using requests to fetch data:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
import requests
import json

# Make a simple API call
response = requests.get('https://api.github.com/repos/python/cpython')
data = response.json()

print(f"Python GitHub Repo Info:")
print(f"- Stars: {data['stargazers_count']:,}")
print(f"- Forks: {data['forks_count']:,}")
print(f"- Open Issues: {data['open_issues_count']:,}")
print(f"- Language: {data['language']}")
print(f"- Created: {data['created_at']}")
"""
                    },
                )
                print_result(result)

                # Test 2: Install and use yfinance
                print("\n2. Testing with 'yfinance' library:")
                print("   Installing yfinance...")
                result = await session.call_tool(
                    name="install_dependencies", arguments={"packages": ["yfinance"]}
                )
                print_result(result)

                print("   Using yfinance to fetch stock data:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
import yfinance as yf
from datetime import datetime, timedelta

# Get Apple stock data
ticker = yf.Ticker("AAPL")

# Get recent price info
info = ticker.info
print(f"Apple Inc. (AAPL) Stock Information:")
print(f"- Current Price: ${info.get('currentPrice', 'N/A')}")
print(f"- Market Cap: ${info.get('marketCap', 0):,}")
print(f"- 52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
print(f"- 52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
print(f"- P/E Ratio: {info.get('trailingPE', 'N/A')}")

# Get historical data for last 5 days
end_date = datetime.now()
start_date = end_date - timedelta(days=5)
history = ticker.history(period="5d")

print("\\nLast 5 days closing prices:")
for date, row in history.iterrows():
    print(f"  {date.strftime('%Y-%m-%d')}: ${row['Close']:.2f}")
"""
                    },
                )
                print_result(result)

                # Test 3: Install and use pandas and numpy
                print("\n3. Testing with 'pandas' and 'numpy':")
                print("   Installing pandas and numpy...")
                result = await session.call_tool(
                    name="install_dependencies",
                    arguments={"packages": ["pandas", "numpy"]},
                )
                print_result(result)

                print("   Data analysis with pandas and numpy:")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = {
    'Date': pd.date_range('2024-01-01', periods=10),
    'Sales': np.random.randint(100, 1000, 10),
    'Costs': np.random.randint(50, 500, 10)
}

df = pd.DataFrame(data)
df['Profit'] = df['Sales'] - df['Costs']

print("Sample Sales Data:")
print(df.head())

print("\\nStatistical Summary:")
print(df[['Sales', 'Costs', 'Profit']].describe().round(2))

print("\\nTotal Performance:")
print(f"Total Sales: ${df['Sales'].sum():,}")
print(f"Total Costs: ${df['Costs'].sum():,}")
print(f"Total Profit: ${df['Profit'].sum():,}")
print(f"Average Daily Profit: ${df['Profit'].mean():.2f}")
print(f"Best Day Profit: ${df['Profit'].max():,}")
print(f"Worst Day Profit: ${df['Profit'].min():,}")
"""
                    },
                )
                print_result(result)

                # Test 4: Multiple dependencies working together
                print("\n4. Testing multiple libraries together:")
                print("   Installing matplotlib...")
                result = await session.call_tool(
                    name="install_dependencies", arguments={"packages": ["matplotlib"]}
                )
                print_result(result)

                print("   Creating data visualization (saving to file):")
                result = await session.call_tool(
                    name="execute_python",
                    arguments={
                        "code": """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Create sample data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=30)
prices = 100 + np.cumsum(np.random.randn(30) * 2)

# Create DataFrame
df = pd.DataFrame({
    'Date': dates,
    'Price': prices,
    'Volume': np.random.randint(1000, 10000, 30)
})

# Calculate moving average
df['MA7'] = df['Price'].rolling(window=7).mean()

# Create plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Price plot
ax1.plot(df['Date'], df['Price'], label='Price', color='blue')
ax1.plot(df['Date'], df['MA7'], label='7-day MA', color='red', linestyle='--')
ax1.set_title('Stock Price with Moving Average')
ax1.set_ylabel('Price ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Volume plot
ax2.bar(df['Date'], df['Volume'], color='green', alpha=0.5)
ax2.set_title('Trading Volume')
ax2.set_xlabel('Date')
ax2.set_ylabel('Volume')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/stock_analysis.png', dpi=100, bbox_inches='tight')
print("Chart saved to /tmp/stock_analysis.png")

# Print summary statistics
print(f"\\nPrice Statistics:")
print(f"Starting Price: ${df['Price'].iloc[0]:.2f}")
print(f"Ending Price: ${df['Price'].iloc[-1]:.2f}")
print(f"Max Price: ${df['Price'].max():.2f}")
print(f"Min Price: ${df['Price'].min():.2f}")
print(f"Total Return: {((df['Price'].iloc[-1] / df['Price'].iloc[0]) - 1) * 100:.2f}%")
"""
                    },
                )
                print_result(result)

                # Test 5: List all installed packages
                print("\n5. Final check - List all installed packages:")
                result = await session.call_tool(
                    name="list_installed_packages", arguments={}
                )
                print_result(result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def print_result(result):
    """Helper function to print tool results."""
    if hasattr(result, "content"):
        for content in result.content:
            if hasattr(content, "text"):
                # Add indentation for better readability
                lines = content.text.split("\n")
                for line in lines:
                    print(f"   {line}")
    else:
        print(f"   Result: {result}")


async def run_all_tests():
    """Run all test suites."""
    print("Starting MCP Python Executor Tests")
    print("=" * 60)

    # Run simple Python tests
    await test_simple_python()

    # Run dependency tests
    await test_with_dependencies()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


async def run_quick_test():
    """Quick test to verify basic functionality."""

    server_params = StdioServerParameters(
        command="docker",
        args=["run", "-i", "--rm", "mcp-python-executor"],
        env=None,
    )

    print("Quick functionality test...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Quick test
                result = await session.call_tool(
                    name="execute_python",
                    arguments={"code": "import sys; print(f'Python {sys.version}')"},
                )

                if hasattr(result, "content"):
                    for content in result.content:
                        if hasattr(content, "text"):
                            print(content.text)

                print("✓ Basic functionality works!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "simple":
            asyncio.run(test_simple_python())
        elif sys.argv[1] == "deps":
            asyncio.run(test_with_dependencies())
        elif sys.argv[1] == "quick":
            asyncio.run(run_quick_test())
        else:
            print("Usage: python test_mcp_python_executor.py [simple|deps|quick]")
    else:
        # Run all tests by default
        asyncio.run(run_all_tests())
