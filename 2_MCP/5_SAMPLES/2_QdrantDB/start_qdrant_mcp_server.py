#!/usr/bin/env python3
"""
QdrantDB MCP Server Startup Script

This script starts the QdrantDB MCP server configured to connect to 
your Docker Qdrant instance running on localhost:6333.

The MCP server will run on localhost:6400 and provide streamable HTTP endpoint
for the client to connect to.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path
import os


def check_qdrant_running():
    """Check if Qdrant is running on localhost:6333"""
    try:
        response = requests.get("http://localhost:6333/", timeout=5)
        return response.status_code == 200
    except:
        return False


def check_mcp_server_running():
    """Check if MCP server is already running on localhost:6400"""
    try:
        response = requests.get("http://localhost:6400/health", timeout=2)
        return True
    except:
        return False


def start_mcp_server():
    """Start the QdrantDB MCP server"""
    
    print("🚀 Starting QdrantDB MCP Server")
    print("=" * 50)
    
    # Check if Qdrant Docker container is running
    print("🔍 Checking Qdrant Docker container...")
    if not check_qdrant_running():
        print("❌ Qdrant is not running on localhost:6333")
        print("Please start Qdrant Docker container first:")
        print("  docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant")
        return False
    
    print("✅ Qdrant is running on localhost:6333")
    
    # Check if MCP server is already running
    if check_mcp_server_running():
        print("⚠️  MCP server appears to be already running on localhost:6400")
        print("If you want to restart it, please stop the existing server first.")
        return True
    
    # Start the MCP server
    print("🔄 Starting QdrantDB MCP server...")
    print("Server will run on: http://localhost:6400")
    print("SSE endpoint: http://localhost:6400/sse")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Set up environment variables
        env = os.environ.copy()
        env.update({
            "QDRANT_URL": "http://localhost:6333",
            "COLLECTION_NAME": "mcp_demo_collection",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "FASTMCP_PORT": "6400",
            "FASTMCP_HOST": "0.0.0.0",
            "FASTMCP_LOG_LEVEL": "INFO",
            "TOOL_STORE_DESCRIPTION": "Store information with metadata in the Qdrant vector database. The 'information' parameter should contain the text content, while 'metadata' should contain additional structured data.",
            "TOOL_FIND_DESCRIPTION": "Search for relevant information in the Qdrant vector database using semantic similarity. The 'query' parameter should describe what you're looking for."
        })
        
        # Start the MCP server with SSE transport
        cmd = [
            "uvx", "mcp-server-qdrant",
            "--transport", "sse"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        print("Environment variables:")
        for key, value in env.items():
            if key.startswith(('QDRANT_', 'COLLECTION_', 'EMBEDDING_', 'FASTMCP_', 'TOOL_')):
                print(f"  {key}={value}")
        
        subprocess.run(cmd, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start MCP server: {e}")
        return False
    except FileNotFoundError:
        print("❌ Required tools not found. Please install:")
        print("  uvx mcp-server-qdrant")
        return False


def main():
    """Main function"""
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    print(f"📁 Working directory: {script_dir}")
    
    success = start_mcp_server()
    
    if success:
        print("\n✅ MCP server setup completed!")
        print("\nNext steps:")
        print("1. Run: python simple_qdrant_client.py")
        print("2. The client will connect to the MCP server")
        print("3. The MCP server will interact with QdrantDB")
    else:
        print("\n❌ Failed to start MCP server")
        sys.exit(1)


if __name__ == "__main__":
    main()