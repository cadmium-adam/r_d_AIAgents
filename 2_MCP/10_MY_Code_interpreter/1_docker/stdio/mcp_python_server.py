#!/usr/bin/env python3
# mcp_python_server.py
import asyncio
import subprocess
import sys
import json
import tempfile
import os
import logging
from typing import Any, Dict, List
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Set up logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # Log to stderr so it doesn't interfere with stdio
)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("python-executor")
logger.info("MCP Python Executor Server starting...")

# Store installed packages
installed_packages = set()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    logger.debug("Listing tools")
    return [
        types.Tool(
            name="install_dependencies",
            description="Install Python packages via pip",
            inputSchema={
                "type": "object",
                "properties": {
                    "packages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of package names to install",
                    }
                },
                "required": ["packages"],
            },
        ),
        types.Tool(
            name="execute_python",
            description="Execute Python code",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"],
            },
        ),
        types.Tool(
            name="list_installed_packages",
            description="List currently installed packages",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool execution."""
    logger.info(f"Calling tool: {name}")

    if name == "install_dependencies":
        packages = arguments.get("packages", [])
        results = []

        for package in packages:
            try:
                logger.info(f"Installing package: {package}")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    installed_packages.add(package)
                    results.append(f"✓ Successfully installed {package}")
                else:
                    results.append(f"✗ Failed to install {package}: {result.stderr}")

            except subprocess.TimeoutExpired:
                results.append(f"✗ Installation of {package} timed out")
            except Exception as e:
                logger.error(f"Error installing {package}: {e}")
                results.append(f"✗ Error installing {package}: {str(e)}")

        return [types.TextContent(type="text", text="\n".join(results))]

    elif name == "execute_python":
        code = arguments.get("code", "")
        logger.debug(f"Executing Python code: {len(code)} characters")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                [sys.executable, temp_file], capture_output=True, text=True, timeout=30
            )

            output = ""
            if result.stdout:
                output += f"Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"Errors:\n{result.stderr}\n"
            if result.returncode != 0:
                output += f"Exit code: {result.returncode}\n"

            return [
                types.TextContent(
                    type="text",
                    text=output if output else "Code executed successfully (no output)",
                )
            ]

        except subprocess.TimeoutExpired:
            return [
                types.TextContent(
                    type="text", text="Execution timed out after 30 seconds"
                )
            ]
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return [types.TextContent(type="text", text=f"Execution error: {str(e)}")]
        finally:
            os.unlink(temp_file)

    elif name == "list_installed_packages":
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            packages = json.loads(result.stdout)
            package_list = [f"{p['name']}=={p['version']}" for p in packages]
            return [
                types.TextContent(
                    type="text", text="Installed packages:\n" + "\n".join(package_list)
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text", text=f"Failed to list packages: {result.stderr}"
                )
            ]

    else:
        logger.warning(f"Unknown tool: {name}")
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP server main loop")

    try:
        # Run the server using stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("stdio server context established")

            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="python-executor",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("MCP Python Executor Server v1.0.0")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
