# test_mcp_local_python_executor_stdio.py
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_simple_python():
    """Test simple Python code execution without dependencies."""

    print("=" * 60)
    print("TEST 1: Simple Python Script (STDIO)")
    print("=" * 60)

    server_params = StdioServerParameters(
        command="python",
        args=["../mcp_python_server.py"],
    )

    try:
        async with stdio_client(server_params) as (read, write):
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
print("Hello from Local MCP STDIO!")
x = 10
y = 20
print(f"The sum of {x} and {y} is {x + y}")
"""
                    },
                )
                print_result(result.content)

                # Test 2: File system operations
                print("\n2. File system operations:")
                result = await session.call_tool(
                    "execute_python",
                    {
                        "code": """
import os

# Create a test file
with open('test_output.txt', 'w') as f:
    f.write('Hello from MCP Local Executor!\\n')
    f.write('This file was created by Python code.\\n')

print('✓ Created test_output.txt')

# Read it back
with open('test_output.txt', 'r') as f:
    content = f.read()

print('Content of test_output.txt:')
print(content)

# Clean up
os.remove('test_output.txt')
print('✓ Cleaned up test_output.txt')
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
    print("TEST 2: Python Scripts with Dependencies (STDIO)")
    print("=" * 60)

    server_params = StdioServerParameters(
        command="python",
        args=["../mcp_python_server.py"],
    )

    try:
        async with stdio_client(server_params) as (read, write):
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
"""
                    },
                )
                print_result(result.content)

                # Test 3: Save data to CSV file
                print("\n3. Save data to CSV file:")
                result = await session.call_tool(
                    "execute_python",
                    {
                        "code": """
import pandas as pd
import numpy as np
import os

# Create sample data
np.random.seed(42)
data = {
    'Date': pd.date_range('2024-01-01', periods=10),
    'Sales': np.random.randint(100, 1000, 10),
    'Costs': np.random.randint(50, 500, 10)
}

df = pd.DataFrame(data)
df['Profit'] = df['Sales'] - df['Costs']

# Save to CSV
csv_file = 'sales_data.csv'
df.to_csv(csv_file, index=False)
print(f"✓ Saved data to {csv_file}")

# Read it back
df_loaded = pd.read_csv(csv_file)
print(f"\\n✓ Loaded data from {csv_file}:")
print(df_loaded.head())

# File size
file_size = os.path.getsize(csv_file)
print(f"\\nFile size: {file_size} bytes")

# Clean up
os.remove(csv_file)
print(f"\\n✓ Cleaned up {csv_file}")
"""
                    },
                )
                print_result(result.content)

                # Test 4: List all installed packages
                print("\n4. Final check - List all installed packages:")
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
    print("Starting MCP Local Python Executor STDIO Tests")
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

    print("Quick functionality test (STDIO)...")

    server_params = StdioServerParameters(
        command="python",
        args=["../mcp_python_server.py"],
    )

    try:
        async with stdio_client(server_params) as (read, write):
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
        elif sys.argv[1] == "deps":
            asyncio.run(test_with_dependencies())
        elif sys.argv[1] == "quick":
            asyncio.run(run_quick_test())
        else:
            print(
                "Usage: python main.py [simple|deps|quick]\n"
                "  simple - Run simple Python tests\n"
                "  deps   - Run tests with dependencies\n"
                "  quick  - Quick functionality test"
            )
    else:
        # Run all tests by default
        asyncio.run(run_all_tests())
