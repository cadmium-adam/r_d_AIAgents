# Human-in-the-Loop (HITL) Example

This example demonstrates how to implement human-in-the-loop functionality using LangChain's agent middleware system. HITL allows you to add human oversight to agent tool calls, pausing execution for review and approval.

## Quick Start

```bash
# Setup
uv venv
source .venv/bin/activate
uv sync

# Run the interactive example
python main.py
```

The example will pause and wait for your input to approve, edit, or reject each action.

## Features

- **Approval-based execution**: Tools can require human approval before execution
- **Three decision types**:
  - ✅ **Approve**: Execute the action as-is
  - ✏️ **Edit**: Modify tool arguments before execution
  - ❌ **Reject**: Reject the action and provide feedback
- **Configurable policies**: Different tools can have different approval requirements
- **Real terminal input**: Uses `input()` to pause and wait for your decisions
- **Persistence**: Uses LangGraph's checkpointing to save state across interrupts

## What the Example Demonstrates

The `main.py` file runs four interactive scenarios:

1. **SQL Query Execution**
   - Requires approval (approve/reject only, no editing for safety)
   - Demonstrates restricting allowed decisions

2. **File Write Operation**
   - Allows all decisions (approve, edit, reject)
   - You can modify the filename or content before execution

3. **Email Sending**
   - Allows all decisions with custom description
   - Demonstrates rejection with feedback

4. **Read Data**
   - Auto-approved (no interrupt)
   - Safe operations don't need approval

## Example Session

```bash
$ python main.py

================================================================================
INTERACTIVE HUMAN-IN-THE-LOOP EXAMPLES
================================================================================

Press Enter to start...

================================================================================
EXAMPLE 1: SQL Query Execution (Approve/Reject Only)
================================================================================

Request: Delete old records from the database where created_at is older than 30 days

Run this example? (y/n): y

--------------------------------------------------------------------------------
Processing...
--------------------------------------------------------------------------------

🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
HUMAN APPROVAL REQUIRED
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

================================================================================
ACTION #1 REQUIRES APPROVAL
================================================================================

Tool: execute_sql
Arguments:
{
  "query": "DELETE FROM records WHERE created_at < NOW() - INTERVAL '30 days';"
}

Description:
🚨 SQL execution requires approval

Allowed decisions: approve, reject

Choose your decision:
  [a] Approve - Execute as-is
  [r] Reject - Reject with feedback

Your choice: a  ← YOU TYPE THIS

✓ Decision recorded: approve

================================================================================
RESUMING EXECUTION WITH YOUR DECISION
================================================================================

--------------------------------------------------------------------------------
RESULT:
--------------------------------------------------------------------------------
Old records have been successfully deleted from the database.
```

## How It Works

### 1. Configure HITL Middleware

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[write_file, execute_sql, read_data, send_email],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # All decisions allowed
                "write_file": True,

                # Only approve/reject (no editing)
                "execute_sql": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "🚨 SQL execution requires approval"
                },

                # Auto-approve (no interrupt)
                "read_data": False,
            }
        )
    ],
    checkpointer=MemorySaver()  # Required for interrupts
)
```

### 2. Invoke Agent

```python
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Your request"}]},
    config={"configurable": {"thread_id": "unique_id"}}
)
```

### 3. Handle Interrupt with Real Input

```python
from human_input import get_human_decisions

if "__interrupt__" in result:
    interrupt_data = result["__interrupt__"][0].value

    # This pauses and waits for terminal input
    decisions = get_human_decisions(interrupt_data)

    # Resume with user's decision
    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config
    )
```

## Decision Interface

When an action requires approval, you'll see:

```
Choose your decision:
  [a] Approve - Execute as-is
  [e] Edit - Modify arguments before execution
  [r] Reject - Reject with feedback

Your choice: _
```

### Approve (a)
Execute the action exactly as proposed.

```
Your choice: a
✓ Decision recorded: approve
```

### Edit (e)
Modify the tool arguments before execution.

```
Your choice: e

Edit mode - modify the arguments
Current arguments:
{
  "filename": "test.txt",
  "content": "Hello"
}

Enter new arguments as JSON (or press Enter to keep current):
> {"filename": "test.txt", "content": "Hello, World!"}

Tool name (or press Enter to keep current):
Current: write_file >

✓ Decision recorded: edit
```

### Reject (r)
Reject the action and provide feedback to the agent.

```
Your choice: r

Rejection feedback (explain why you're rejecting):
> This operation is too risky. Please use the archive function instead.

✓ Decision recorded: reject
```

## Key Concepts

### Interrupt Configuration

Control which tools require approval:

```python
interrupt_on={
    # All decisions allowed (approve, edit, reject)
    "tool_name": True,

    # Specific decisions with custom description
    "tool_name": {
        "allowed_decisions": ["approve", "reject"],  # No editing
        "description": "Custom approval message"
    },

    # Auto-approve (no interrupt)
    "tool_name": False,
}
```

### Checkpointing

HITL requires a checkpointer to persist state:

```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_agent(
    ...,
    checkpointer=MemorySaver()  # Use AsyncPostgresSaver in production
)
```

### Thread IDs

Each conversation needs a unique thread ID to maintain state:

```python
config = {"configurable": {"thread_id": "unique_conversation_id"}}
```

## Files

- **main.py** - Interactive example with 4 scenarios
- **tools.py** - Tool definitions (write_file, execute_sql, read_data, send_email)
- **human_input.py** - Terminal input handler with `input()` calls
- **.env** - OpenAI API key
- **pyproject.toml** - Dependencies

## Dependencies

- `langchain>=1.0.2` - Core agent framework
- `langgraph>=1.0.2` - Graph-based execution and interrupts
- `python-dotenv>=1.1.0` - Environment variable management

## Production Considerations

For production deployment:

1. **Persistent Checkpointer**: Use `AsyncPostgresSaver` instead of `MemorySaver`
2. **Web UI**: Build a web interface instead of terminal `input()`
3. **Timeouts**: Add timeout handling for pending approvals
4. **Audit Trail**: Log all decisions for compliance
5. **Notifications**: Alert reviewers when approval is needed
6. **Role-Based Access**: Different users approve different tool types

## References

- [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
- [LangGraph Interrupts](https://docs.langchain.com/oss/langgraph/interrupts)
