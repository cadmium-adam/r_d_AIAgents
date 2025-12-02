import os
import json
import math
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

# Step 1: Get user input and send with tool definition
user_input = input("Enter your math question: ")
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
        result = calculate(args["expression"])
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
