import subprocess
import sys
import json
import tempfile
import os
import logging
import uvicorn
import contextlib
from collections.abc import AsyncIterator
from typing import Any, Dict, List
from mcp.server import Server
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


PORT = 8055


def serve():

    # Initialize the MCP server
    server = Server("python-executor")
    logger.info("MCP Python Executor HTTP Server starting...")

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
                        "code": {
                            "type": "string",
                            "description": "Python code to execute",
                        }
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
                        results.append(
                            f"✗ Failed to install {package}: {result.stderr}"
                        )

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
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
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
                        text=(
                            output
                            if output
                            else "Code executed successfully (no output)"
                        ),
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
                return [
                    types.TextContent(type="text", text=f"Execution error: {str(e)}")
                ]
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
                        type="text",
                        text="Installed packages:\n" + "\n".join(package_list),
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

    # ---------------------------------
    # HTTP Server Transport
    # ---------------------------------

    # Create the session manager with our app and event store
    # Set stateless=False to maintain persistent connections and avoid ClosedResourceError
    session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=True,  # Use JSON responses
        event_store=None,  # No resumability
        stateless=False,  # Keep connections open to avoid premature closure
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            print("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                print("Application shutting down...")

    # Create Starlette app
    starlette_app = Starlette(
        debug=False,
        routes=[
            Mount("/mcp/", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logger.info("MCP Python Executor HTTP Server v1.0.0")
    logger.info(f"Starting HTTP server on 0.0.0.0:{PORT}")

    print("Starting server...")
    try:
        serve()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cleaning up before exit...")
