"""Interactive Human-in-the-Loop example using LangChain agent with middleware."""

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from tools import write_file, execute_sql, read_data, send_email
from human_input import get_human_decisions

# Load environment variables
load_dotenv()


def run_example(agent, example_num: int, title: str, user_request: str):
    """Run a single interactive example.

    Args:
        agent: The agent with HITL middleware
        example_num: Example number (1, 2, 3, 4)
        title: Title of the example
        user_request: The user's request to the agent
    """
    print()
    print("=" * 80)
    print(f"EXAMPLE {example_num}: {title}")
    print("=" * 80)
    print()
    print(f"Request: {user_request}")
    print()

    # Ask user if they want to run this example
    run = input("Run this example? (y/n): ").strip().lower()

    if run != 'y':
        print("Skipped.")
        return

    print()
    print("-" * 80)
    print("Processing...")
    print("-" * 80)
    print()

    config = {"configurable": {"thread_id": f"example_{example_num}"}}

    # Invoke agent
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_request}]},
        config=config,
    )

    # Check if there's an interrupt requiring human approval
    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value

        # Get real human decisions via terminal input
        decisions = get_human_decisions(interrupt_data)

        print()
        print("=" * 80)
        print("RESUMING EXECUTION WITH YOUR DECISION")
        print("=" * 80)
        print()

        # Resume with human's decision
        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=config,
        )

    # Display the final result
    print()
    print("-" * 80)
    print("RESULT:")
    print("-" * 80)
    if "messages" in result:
        last_message = result["messages"][-1]
        print(last_message.content)
    else:
        print("Task completed successfully!")
    print()


def main():
    """Run interactive human-in-the-loop examples."""

    print()
    print("=" * 80)
    print("INTERACTIVE HUMAN-IN-THE-LOOP EXAMPLES")
    print("=" * 80)
    print()
    print("This will demonstrate different HITL scenarios.")
    print("You'll be asked to approve, edit, or reject each action.")
    print()
    print("Press Ctrl+C at any time to exit.")
    print()
    input("Press Enter to start...")

    # Create agent with HITL middleware
    agent = create_agent(
        model="openai:gpt-4o-mini",
        tools=[write_file, execute_sql, read_data, send_email],
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    # Allow all decisions for write_file (approve, edit, reject)
                    "write_file": True,

                    # Only allow approve/reject for execute_sql (no editing)
                    "execute_sql": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "🚨 SQL execution requires approval",
                    },

                    # Custom description for send_email
                    "send_email": {
                        "allowed_decisions": ["approve", "edit", "reject"],
                        "description": "📧 Email requires review before sending",
                    },

                    # Safe operation - no approval needed
                    "read_data": False,
                },
                description_prefix="Tool execution pending approval",
            ),
        ],
        # HITL requires checkpointing to handle interrupts
        checkpointer=MemorySaver(),
    )

    # Example 1: SQL execution (approve/reject only, no editing)
    run_example(
        agent,
        1,
        "SQL Query Execution (Approve/Reject Only)",
        "Delete old records from the database where created_at is older than 30 days"
    )

    # Example 2: File write (allows editing)
    run_example(
        agent,
        2,
        "File Write Operation (Can Edit)",
        "Write a greeting message to a file called hello.txt"
    )

    # Example 3: Email sending (can reject with feedback)
    run_example(
        agent,
        3,
        "Email Sending (Can Reject with Feedback)",
        "Send an email to boss@company.com saying I quit"
    )

    # Example 4: Read data (auto-approved, no interrupt)
    run_example(
        agent,
        4,
        "Read Data (Auto-Approved)",
        "Read data from the database"
    )

    print()
    print("=" * 80)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 80)
    print()
    print("You've experienced:")
    print("  ✅ Approve - Execute as-is")
    print("  ✏️  Edit - Modify before execution")
    print("  ❌ Reject - Reject with feedback")
    print("  🚀 Auto-approve - Safe operations need no approval")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("Interrupted by user. Goodbye!")
    except Exception as e:
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
