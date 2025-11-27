"""Example tools for human-in-the-loop demonstration."""

from langchain_core.tools import tool


@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file.

    Args:
        filename: The name of the file to write
        content: The content to write to the file

    Returns:
        Success message
    """
    try:
        with open(filename, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"


@tool
def execute_sql(query: str) -> str:
    """Execute a SQL query (simulated).

    Args:
        query: The SQL query to execute

    Returns:
        Query result (simulated)
    """
    # This is a simulated SQL execution for demonstration
    # In a real scenario, you would connect to a database
    return f"Simulated execution of query: {query}\nResult: Query executed successfully (simulated)"


@tool
def read_data(source: str) -> str:
    """Read data from a source (safe operation).

    Args:
        source: The source to read from

    Returns:
        Data from the source
    """
    # Simulated read operation
    return f"Reading data from {source}: Sample data here..."


@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email (simulated).

    Args:
        recipient: Email address of the recipient
        subject: Email subject
        body: Email body

    Returns:
        Success message
    """
    # Simulated email sending
    return f"Email sent to {recipient}\nSubject: {subject}\nBody: {body}"
