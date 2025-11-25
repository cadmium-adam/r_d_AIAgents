# Custom component/node

```python
from langflow.custom.custom_component.component import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message


class UppercaseComponent(Component):
    display_name = "Uppercase Converter"
    description = "Converts input text to uppercase."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "arrow-up"
    name = "UppercaseComponent"
    base_classes = ["Message"]

    inputs = [
        MessageTextInput(
            name="input_value",
            display_name="Input Value",
            info="Text to convert to uppercase.",
            value="Hello World!",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Output Message", name="message", method="build_message"),
    ]

    def build_message(self) -> Message:
        text = (self.input_value or "").upper()
        self.status = text
        return Message(text=text)

```
