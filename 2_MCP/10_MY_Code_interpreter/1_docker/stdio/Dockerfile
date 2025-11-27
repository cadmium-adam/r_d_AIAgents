FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m -s /bin/bash mcp

# Set working directory
WORKDIR /app

# Copy the requirements file first (for better caching)
COPY requirements.txt .

# Install base Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server files
COPY mcp_python_server.py .

# Make sure the script is executable
RUN chmod +x mcp_python_server.py

# Switch to non-root user
USER mcp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use exec form to ensure proper signal handling
ENTRYPOINT ["python", "-u", "mcp_python_server.py"]