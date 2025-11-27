# test_mcp_python_executor_http.py
import asyncio

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


async def test_simple_python():
    """Test simple Python code execution without dependencies."""

    print("=" * 60)
    print("TEST 1: Simple Python Script (HTTP)")
    print("=" * 60)

    server_url = "http://localhost:8055"

    try:
        async with streamablehttp_client(f"{server_url}/mcp/", auth=None) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                # Initialize
                result = await session.initialize()
                print(f"✓ Initialize result: {result.serverInfo}")

                # Test ping
                ping_result = await session.send_ping()
                print(f"✓ Ping successful")

                # List tools
                tools_list = await session.list_tools()
                print(f"✓ Available tools: {len(tools_list.tools)}")
                for tool in tools_list.tools:
                    print(f"   - {tool.name}: {tool.description}")

                # Test 1: Basic print and arithmetic
                print("\n1. Basic print and arithmetic:")
                result = await session.call_tool(
                    "execute_python",
                    {
                        "code": """
print("Hello from MCP HTTP!")
x = 10
y = 20
print(f"The sum of {x} and {y} is {x + y}")
"""
                    },
                )
                print_result(result.content)

                # Test 2: Functions and loops
                print("\n2. Functions and loops:")
                result = await session.call_tool(
                    "execute_python",
                    {
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
                print_result(result.content)

                # Test 3: Working with built-in modules
                print("\n3. Built-in modules (datetime, random, math):")
                result = await session.call_tool(
                    "execute_python",
                    {
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
                print_result(result.content)

                # Test 4: Error handling
                print("\n4. Error handling test:")
                result = await session.call_tool(
                    "execute_python",
                    {
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
                print_result(result.content)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


async def test_streaming():
    """Test streaming execution."""

    print("\n" + "=" * 60)
    print("TEST 2: Streaming Execution")
    print("=" * 60)

    server_url = "http://localhost:8055"

    try:
        async with streamablehttp_client(f"{server_url}/mcp/", auth=None) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                print("✓ Connected to MCP server")

                # Initialize
                await session.initialize()

                print("\n1. Streaming execution test:")
                result = await session.call_tool(
                    "execute_python",
                    {
                        "code": """
import time
for i in range(5):
    print(f"Count: {i}")
    time.sleep(0.5)
print("Done!")
"""
                    },
                )
                print_result(result.content)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


async def test_with_dependencies():
    """Test Python code execution with external dependencies."""

    print("\n" + "=" * 60)
    print("TEST 3: Python Scripts with Dependencies (HTTP)")
    print("=" * 60)

    server_url = "http://localhost:8055"

    try:
        async with streamablehttp_client(f"{server_url}/mcp/", auth=None) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                print("✓ Connected to MCP server")

                # Initialize
                await session.initialize()

                # Test 1: Install and use requests
                print("\n1. Testing with 'requests' library:")
                print("   Installing requests...")
                result = await session.call_tool(
                    "install_dependencies", {"packages": ["requests"]}
                )
                print_result(result.content)

                print("   Using requests to fetch data:")
                result = await session.call_tool(
                    "execute_python",
                    {
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
                print_result(result.content)

                # Test 2: Install and use pandas and numpy
                print("\n2. Testing with 'pandas' and 'numpy':")
                print("   Installing pandas and numpy...")
                result = await session.call_tool(
                    "install_dependencies",
                    {"packages": ["pandas", "numpy"]},
                )
                print_result(result.content)

                print("   Data analysis with pandas and numpy:")
                result = await session.call_tool(
                    "execute_python",
                    {
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
                print_result(result.content)

                # Test 3: List all installed packages
                print("\n3. Final check - List all installed packages:")
                result = await session.call_tool("list_installed_packages", {})
                print_result(result.content)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def print_result(content):
    """Helper function to print tool results."""
    for item in content:
        if hasattr(item, "text"):
            # Add indentation for better readability
            lines = item.text.split("\n")
            for line in lines:
                print(f"   {line}")
        else:
            print(f"   {item}")


async def run_all_tests():
    """Run all test suites."""
    print("Starting MCP Python Executor HTTP Tests")
    print("=" * 60)

    # Run simple Python tests
    await test_simple_python()

    # Run streaming tests
    await test_streaming()

    # Run dependency tests
    await test_with_dependencies()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


async def run_quick_test():
    """Quick test to verify basic functionality."""

    print("Quick functionality test (HTTP)...")

    server_url = "http://localhost:8055"

    try:
        async with streamablehttp_client(f"{server_url}/mcp/", auth=None) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                # Initialize
                result = await session.initialize()
                print(f"✓ Server initialized: {result.serverInfo}")

                # Quick test
                result = await session.call_tool(
                    "execute_python",
                    {"code": "import sys; print(f'Python {sys.version}')"},
                )

                print_result(result.content)

                print("✓ Basic functionality works!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "simple":
            asyncio.run(test_simple_python())
        elif sys.argv[1] == "stream":
            asyncio.run(test_streaming())
        elif sys.argv[1] == "deps":
            asyncio.run(test_with_dependencies())
        elif sys.argv[1] == "quick":
            asyncio.run(run_quick_test())
        else:
            print(
                "Usage: python main.py [simple|stream|deps|quick]\n"
                "  simple - Run simple Python tests\n"
                "  stream - Run streaming tests\n"
                "  deps   - Run tests with dependencies\n"
                "  quick  - Quick functionality test"
            )
    else:
        # Run all tests by default
        asyncio.run(run_all_tests())
