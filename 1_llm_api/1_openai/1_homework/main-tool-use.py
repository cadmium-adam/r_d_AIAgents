import os
import json
import math
import urllib.request
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define a calculator tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation. Use Python math syntax: cos(), sin(), tan(), sqrt(), pi, radians(), etc. Angles must be in radians, use radians(30) for 30 degrees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g. '2 + 2 * 3'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current UTC time from the internet",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# The actual function implementation
def calculate(expression: str) -> str:
    try:
        # Make math functions available for eval
        result = eval(expression, {"__builtins__": {}}, vars(math))
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def get_current_time() -> str:
    try:
        response = urllib.request.urlopen('https://timeapi.io/api/time/current/zone?timeZone=UTC')
        data = json.loads(response.read())
        return f"{data['date']} {data['time']} UTC"
    except Exception as e:
        # Fallback to local system UTC time
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# Step 1: Get user input and send with tool definition
user_input = input("Enter your question: ")
messages = [{"role": "user", "content": user_input}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)

assistant_message = response.choices[0].message
print("--- LLM Response (with tool call): ---")
print(assistant_message)

# Step 2: If LLM wants to use a tool, execute it
if assistant_message.tool_calls:
    messages.append(assistant_message)

    for tool_call in assistant_message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        if tool_call.function.name == "calculate":
            result = calculate(args["expression"])
        elif tool_call.function.name == "get_current_time":
            result = get_current_time()
        else:
            result = "Unknown tool"
        print(f"\n--- Tool executed: {tool_call.function.name}({args}) = {result} ---")

        # Step 3: Send tool result back to LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    # Step 4: Get final response from LLM
    final_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    print("\n--- Final LLM Response: ---")
    print(final_response.choices[0].message.content)
else:
    print("\n--- No tool call, direct response: ---")
    print(assistant_message.content)
