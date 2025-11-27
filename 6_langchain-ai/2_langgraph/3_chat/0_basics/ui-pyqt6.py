import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

# Import your existing code (be sure to wrap it so it doesn't run the CLI part)
from graph import my_graph  

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LangGraph Chatbot (PyQt6)")

        # Layouts
        self.layout = QVBoxLayout(self)
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.input_line)
        h_layout.addWidget(self.send_button)

        self.layout.addWidget(QLabel("Chat:"))
        self.layout.addWidget(self.chat_display)
        self.layout.addLayout(h_layout)

    def send_message(self):
        user_text = self.input_line.text().strip()
        if not user_text:
            return
        self.append_chat("User", user_text)
        self.input_line.clear()
        self.process_bot_reply(user_text)

    def append_chat(self, who, text):
        self.chat_display.append(f"<b>{who}:</b> {text}")

    def process_bot_reply(self, user_text):
        # Stream reply from the graph
        try:
            for event in my_graph.stream({"messages": [("user", user_text)]}):
                for value in event.values():
                    reply = value["messages"][-1].content
                    self.append_chat("Assistant", reply)
        except Exception as e:
            self.append_chat("System", f"<font color='red'>Error: {e}</font>")

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
