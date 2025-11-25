# 1_sequential

## Uppercase node

```python
from langflow.custom.custom_component.component import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message


class UpperCaseComponent(Component):
    display_name = "Step 1: Uppercase"
    description = "Step 1: Converts input to uppercase and stores in message metadata"
    icon = "type"
    name = "UpperCaseComponent"

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input Text",
            info="Text to convert to uppercase",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Uppercase Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Message:
        # Convert to uppercase
        uppercase_text = self.input_value.upper()

        self.status = f"✓ Step 1 Complete: '{self.input_value}' → '{uppercase_text}'"

        # Store results in the message metadata for downstream components
        return Message(
            text=uppercase_text,
            metadata={
                "original_input": self.input_value,
                "step1_output": uppercase_text,
                "step": "1"
            }
        )
```

## Reverse node

```python
from langflow.custom.custom_component.component import Component
from langflow.io import MessageInput, Output
from langflow.schema.message import Message


class ReverseComponent(Component):
    display_name = "Step 2: Reverse"
    description = "Step 2: Reverses the text and accesses shared state via metadata"
    icon = "rotate-ccw"
    name = "ReverseComponent"

    inputs = [
        MessageInput(
            name="input_message",
            display_name="Input Message",
            info="Message to reverse",
        ),
    ]

    outputs = [
        Output(display_name="Reversed Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Message:
        # Get text from input message
        input_text = self.input_message.text if hasattr(self.input_message, 'text') else str(self.input_message)

        # Reverse the text
        reversed_text = input_text[::-1]

        # Try to get metadata from previous step
        metadata = {}
        if hasattr(self.input_message, 'metadata') and self.input_message.metadata:
            metadata = self.input_message.metadata.copy()

        # Add current step info
        metadata.update({
            "step2_output": reversed_text,
            "step2_input": input_text,
            "step": "2"
        })

        # Get info from previous steps for status
        original = metadata.get("original_input", "unknown")
        step1_result = metadata.get("step1_output", input_text)

        self.status = f"✓ Step 2 Complete: '{step1_result}' → '{reversed_text}' (Original: '{original}')"

        return Message(
            text=reversed_text,
            metadata=metadata
        )
```

## Summary node

```python
from langflow.custom.custom_component.component import Component
from langflow.io import MessageInput, Output
from langflow.schema.message import Message


class SummaryComponent(Component):
    display_name = "Step 3: Summary"
    description = "Step 3: Creates a summary by accessing all metadata from previous steps"
    icon = "file-text"
    name = "SummaryComponent"

    inputs = [
        MessageInput(
            name="input_message",
            display_name="Input Message",
            info="Message to summarize",
        ),
    ]

    outputs = [
        Output(display_name="Summary Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Message:
        # Get text from input message
        input_text = self.input_message.text if hasattr(self.input_message, 'text') else str(self.input_message)

        # Retrieve all previous steps from metadata
        metadata = {}
        if hasattr(self.input_message, 'metadata') and self.input_message.metadata:
            metadata = self.input_message.metadata.copy()

        original = metadata.get("original_input", "unknown")
        step1 = metadata.get("step1_output", "unknown")
        step2 = metadata.get("step2_output", "unknown")

        # Create a comprehensive summary showing the sequential workflow
        summary = "=" * 60 + "\n"
        summary += "SEQUENTIAL WORKFLOW SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        summary += f"📝 Original Input:        '{original}'\n"
        summary += f"⬆️  After Step 1 (Upper):  '{step1}'\n"
        summary += f"🔄 After Step 2 (Reverse): '{step2}'\n"
        summary += f"✅ Final Result:          '{input_text}'\n\n"
        summary += "=" * 60 + "\n"
        summary += "All steps completed successfully!\n"
        summary += "State passed via Message metadata.\n"
        summary += "=" * 60

        # Add final step info to metadata
        metadata.update({
            "final_output": input_text,
            "workflow_complete": True,
            "step": "3"
        })

        self.status = "✓ Workflow Complete - All steps executed sequentially"

        return Message(
            text=summary,
            metadata=metadata
        )
```
