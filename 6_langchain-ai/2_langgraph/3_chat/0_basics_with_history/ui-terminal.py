from graph import my_graph

# ---------------------------
# Run the graph
# ---------------------------

messages = (
    []
)  # <--------------------------------------------------------- Store chat history

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    # Add user's message to the history
    messages.append(
        ("user", user_input)
    )  # <--------------------------------------------------------- Store user message

    for event in my_graph.stream({"messages": messages}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            assistant_reply = value["messages"][-1].content
            # Add assistant's message to the history
            messages.append(
                ("assistant", assistant_reply)
            )  # <--------------------------------------------------------- Store assistant reply
