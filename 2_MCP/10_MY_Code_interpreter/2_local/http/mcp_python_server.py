import subprocess
import sys
import json
import tempfile
import os
import logging
import uvicorn
import contextlib
from pathlib import Path
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


PORT = 8056


class VirtualEnvironmentManager:
    """Manages a virtual environment for code execution using uv."""

    def __init__(self, venv_path: str = "./.venv", work_dir: str = "./code_temp"):
        self.venv_path = Path(venv_path).resolve()
        self.work_dir = Path(work_dir).resolve()
        self.python_executable = None
        self._initialized = False

    def initialize(self):
        """Create and initialize the virtual environment if it doesn't exist using uv."""
        if self._initialized:
            return

        try:
            if not self.venv_path.exists():
                logger.info(f"Creating virtual environment with uv at {self.venv_path}")
                subprocess.run(
                    ["uv", "venv", str(self.venv_path)],
                    check=True,
                    capture_output=True
                )

            # Create work directory for code execution
            if not self.work_dir.exists():
                logger.info(f"Creating work directory at {self.work_dir}")
                self.work_dir.mkdir(parents=True, exist_ok=True)

            # Determine the Python executable path
            if sys.platform == "win32":
                self.python_executable = self.venv_path / "Scripts" / "python.exe"
            else:
                self.python_executable = self.venv_path / "bin" / "python"

            if not self.python_executable.exists():
                raise RuntimeError(f"Virtual environment Python not found at {self.python_executable}")

            logger.info(f"Virtual environment ready at {self.venv_path}")
            logger.info(f"Python executable: {self.python_executable}")
            logger.info(f"Work directory: {self.work_dir}")
            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize virtual environment: {e}")
            raise

    def install_package(self, package: str, timeout: int = 60) -> tuple[bool, str]:
        """Install a package in the virtual environment using uv."""
        if not self._initialized:
            self.initialize()

        try:
            logger.info(f"Installing package: {package}")
            result = subprocess.run(
                ["uv", "pip", "install", "--python", str(self.python_executable), package],
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            if result.returncode == 0:
                return True, f"Successfully installed {package}"
            else:
                return False, f"Failed to install {package}: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, f"Installation of {package} timed out"
        except Exception as e:
            logger.error(f"Error installing {package}: {e}")
            return False, f"Error installing {package}: {str(e)}"

    def list_packages(self) -> tuple[bool, str]:
        """List all installed packages in the virtual environment using uv."""
        if not self._initialized:
            self.initialize()

        try:
            result = subprocess.run(
                ["uv", "pip", "list", "--python", str(self.python_executable), "--format=json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                package_list = [f"{p['name']}=={p['version']}" for p in packages]
                return True, "Installed packages:\n" + "\n".join(package_list)
            else:
                return False, f"Failed to list packages: {result.stderr}"

        except Exception as e:
            logger.error(f"Error listing packages: {e}")
            return False, f"Error listing packages: {str(e)}"

    def execute_code(self, code: str, timeout: int = 30) -> tuple[bool, str]:
        """Execute Python code in the virtual environment.

        Code runs in the work_dir (code_temp), so all file operations
        happen in that directory.
        """
        if not self._initialized:
            self.initialize()

        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            result = subprocess.run(
                [str(self.python_executable), temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.work_dir),  # Execute in code_temp directory
            )

            output = ""
            if result.stdout:
                output += f"Output:\n{result.stdout}\n"
            if result.stderr:
                output += f"Errors:\n{result.stderr}\n"
            if result.returncode != 0:
                output += f"Exit code: {result.returncode}\n"

            success = result.returncode == 0
            return success, output if output else "Code executed successfully (no output)"

        except subprocess.TimeoutExpired:
            return False, f"Execution timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return False, f"Execution error: {str(e)}"
        finally:
            os.unlink(temp_file)


def serve():
    """Main server function."""

    # Initialize the MCP server
    server = Server("local-python-executor")
    logger.info("MCP Local Python Executor HTTP Server starting...")

    # Initialize virtual environment manager
    venv_manager = VirtualEnvironmentManager()
    venv_manager.initialize()

    @server.list_tools()
    async def handle_list_tools() -> List[types.Tool]:
        """List available tools."""
        logger.debug("Listing tools")
        return [
            types.Tool(
                name="install_dependencies",
                description="Install Python packages via pip in a local virtual environment",
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
                description="Execute Python code in a local virtual environment with filesystem access",
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
                description="List currently installed packages in the virtual environment",
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
                success, message = venv_manager.install_package(package)
                results.append(f"{'✓' if success else '✗'} {message}")

            return [types.TextContent(type="text", text="\n".join(results))]

        elif name == "execute_python":
            code = arguments.get("code", "")
            logger.debug(f"Executing Python code: {len(code)} characters")

            success, output = venv_manager.execute_code(code)
            return [types.TextContent(type="text", text=output)]

        elif name == "list_installed_packages":
            success, output = venv_manager.list_packages()
            return [types.TextContent(type="text", text=output)]

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
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    # Run the server
    uvicorn.run(starlette_app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logger.info("MCP Local Python Executor HTTP Server v1.0.0")
    logger.info(f"Starting HTTP server on 0.0.0.0:{PORT}")

    print("Starting server...")
    try:
        serve()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Cleaning up before exit...")
