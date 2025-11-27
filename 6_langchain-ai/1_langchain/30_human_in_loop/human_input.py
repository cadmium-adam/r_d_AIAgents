"""Interactive human input handler for HITL decisions."""

import json
from typing import Any


def display_action_request(action_request: dict[str, Any], review_config: dict[str, Any], index: int) -> None:
    """Display an action request to the user."""
    print()
    print("=" * 80)
    print(f"ACTION #{index + 1} REQUIRES APPROVAL")
    print("=" * 80)
    print()
    print(f"Tool: {action_request['name']}")
    print()
    print("Arguments:")
    print(json.dumps(action_request['args'], indent=2))
    print()
    if 'description' in action_request:
        print("Description:")
        print(action_request['description'])
        print()
    print(f"Allowed decisions: {', '.join(review_config['allowed_decisions'])}")
    print()


def get_human_decision(action_request: dict[str, Any], review_config: dict[str, Any]) -> dict[str, Any]:
    """Get a decision from the human user via terminal input.

    Args:
        action_request: The action requiring approval
        review_config: Configuration for allowed decisions

    Returns:
        Decision dictionary (approve, edit, or reject)
    """
    allowed_decisions = review_config['allowed_decisions']

    while True:
        print("Choose your decision:")
        print("  [a] Approve - Execute as-is")
        if 'edit' in allowed_decisions:
            print("  [e] Edit - Modify arguments before execution")
        if 'reject' in allowed_decisions:
            print("  [r] Reject - Reject with feedback")
        print()

        choice = input("Your choice: ").strip().lower()

        if choice == 'a' and 'approve' in allowed_decisions:
            return {"type": "approve"}

        elif choice == 'e' and 'edit' in allowed_decisions:
            print()
            print("Edit mode - modify the arguments")
            print("Current arguments:")
            print(json.dumps(action_request['args'], indent=2))
            print()
            print("Enter new arguments as JSON (or press Enter to keep current):")

            # Try to get edited arguments
            while True:
                try:
                    new_args_input = input("> ").strip()

                    if not new_args_input:
                        # Keep current arguments
                        new_args = action_request['args']
                        break

                    # Parse JSON
                    new_args = json.loads(new_args_input)
                    break

                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")
                    print("Try again (or press Enter to keep current arguments):")

            print()
            print("Tool name (or press Enter to keep current):")
            new_name = input(f"Current: {action_request['name']} > ").strip()

            if not new_name:
                new_name = action_request['name']

            return {
                "type": "edit",
                "edited_action": {
                    "name": new_name,
                    "args": new_args
                }
            }

        elif choice == 'r' and 'reject' in allowed_decisions:
            print()
            print("Rejection feedback (explain why you're rejecting):")
            message = input("> ").strip()

            if not message:
                message = f"Action '{action_request['name']}' was rejected by the user."

            return {
                "type": "reject",
                "message": message
            }

        else:
            print()
            print(f"Invalid choice '{choice}'. Please choose from the allowed decisions.")
            print()


def get_human_decisions(interrupt_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Get decisions for all actions requiring approval.

    Args:
        interrupt_data: The interrupt data with action_requests and review_configs

    Returns:
        List of decisions, one per action
    """
    action_requests = interrupt_data['action_requests']
    review_configs = interrupt_data['review_configs']

    print()
    print("🚨" * 40)
    print("HUMAN APPROVAL REQUIRED")
    print("🚨" * 40)
    print()
    print(f"Number of actions requiring approval: {len(action_requests)}")

    decisions = []

    for i, (action_request, review_config) in enumerate(zip(action_requests, review_configs)):
        display_action_request(action_request, review_config, i)
        decision = get_human_decision(action_request, review_config)
        decisions.append(decision)

        print()
        print(f"✓ Decision recorded: {decision['type']}")

        if i < len(action_requests) - 1:
            print()
            print("-" * 80)
            print("Next action...")
            print("-" * 80)

    return decisions


def display_simple_prompt(action_request: dict[str, Any], review_config: dict[str, Any]) -> dict[str, Any]:
    """Simple one-line prompt for quick decisions.

    Args:
        action_request: The action requiring approval
        review_config: Configuration for allowed decisions

    Returns:
        Decision dictionary
    """
    allowed = review_config['allowed_decisions']
    options = []

    if 'approve' in allowed:
        options.append("a=approve")
    if 'edit' in allowed:
        options.append("e=edit")
    if 'reject' in allowed:
        options.append("r=reject")

    print()
    print(f"⚠️  {action_request['name']} with {action_request['args']}")

    choice = input(f"Decision ({', '.join(options)}): ").strip().lower()

    if choice == 'a' and 'approve' in allowed:
        return {"type": "approve"}
    elif choice == 'e' and 'edit' in allowed:
        print("Enter new args as JSON:")
        new_args = json.loads(input("> "))
        return {"type": "edit", "edited_action": {"name": action_request['name'], "args": new_args}}
    elif choice == 'r' and 'reject' in allowed:
        message = input("Rejection reason: ")
        return {"type": "reject", "message": message or "Rejected by user"}
    else:
        print("Invalid choice, defaulting to reject")
        return {"type": "reject", "message": "Invalid input, action rejected"}
