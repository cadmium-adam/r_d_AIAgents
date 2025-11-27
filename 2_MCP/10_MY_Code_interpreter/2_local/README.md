# MCP Local Python Code Interpreter

A Model Context Protocol (MCP) server that executes Python code locally in a virtual environment with full filesystem access.

## Features

- **Virtual Environment Isolation**: Runs code in a dedicated Python virtual environment managed by `uv`
- **Package Management**: Install and manage Python packages via `uv pip`
- **Filesystem Access**: Full read/write access to the local filesystem
- **Multiple Transports**: Available in both STDIO and HTTP versions
- **Package Persistence**: Installed packages persist between sessions in the virtual environment
- **Fast Package Installation**: Uses `uv` for blazing-fast package installations

## Architecture

```
2_local/
├── stdio/                    # STDIO transport version
│   ├── mcp_python_server.py  # Server implementation
│   ├── pyproject.toml        # Project dependencies
│   ├── .venv/                # Virtual environment (auto-created)
│   ├── code_temp/            # Working directory for code execution (auto-created)
│   └── test/
│       ├── main.py           # Test client
│       └── pyproject.toml    # Test dependencies
└── http/                     # HTTP transport version
    ├── mcp_python_server.py  # Server implementation
    ├── pyproject.toml        # Project dependencies
    ├── .venv/                # Virtual environment (auto-created)
    ├── code_temp/            # Working directory for code execution (auto-created)
    └── test/
        ├── main.py           # Test client
        └── pyproject.toml    # Test dependencies
```

## Available Tools

### 1. `install_dependencies`
Install Python packages via `uv pip` in the local virtual environment.

**Parameters:**
- `packages` (array of strings): List of package names to install

**Example:**
```json
{
  "packages": ["requests", "pandas", "numpy"]
}
```

### 2. `execute_python`
Execute Python code in the local virtual environment with filesystem access.

All file operations (create, read, write) happen in the `code_temp` directory.

**Parameters:**
- `code` (string): Python code to execute

**Example:**
```json
{
  "code": "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})\ndf.to_csv('output.csv')"
}
```

**Note:** Files created by the code are saved in the `code_temp/` directory.

### 3. `list_installed_packages`
List all packages currently installed in the virtual environment.

**Parameters:** None

## Usage

### STDIO Version

#### Running the Server

1. **Setup with uv:**
   ```bash
   cd stdio
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

2. **Run the server:**
   ```bash
   python mcp_python_server.py
   ```

#### Testing the Server

```bash
cd stdio/test
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
python main.py quick
```

### HTTP Version

#### Running the Server

1. **Setup with uv:**
   ```bash
   cd http
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

2. **Run the server:**
   ```bash
   python mcp_python_server.py
   ```

   Server will start on `http://localhost:8056`

#### Testing the Server

```bash
cd http/test
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
python main.py quick
```

## Test Suites

Both STDIO and HTTP versions include comprehensive test suites:

### Run All Tests
```bash
python main.py
```

### Run Specific Test Suites

**Simple Python Tests:**
```bash
python main.py simple
```
Tests basic Python functionality, arithmetic, and built-in modules.

**Dependency Tests:**
```bash
python main.py deps
```
Tests package installation and usage (requests, pandas, numpy).

**Quick Test:**
```bash
python main.py quick
```
Quick functionality check to verify the server is working.

## Example Usage

### Install and Use Packages

```python
# Install pandas and numpy
await session.call_tool(
    "install_dependencies",
    {"packages": ["pandas", "numpy"]}
)

# Use the installed packages
await session.call_tool(
    "execute_python",
    {
        "code": """
import pandas as pd
import numpy as np

data = {'values': np.random.rand(5)}
df = pd.DataFrame(data)
print(df)
"""
    }
)
```

### File System Operations

```python
# Create and manipulate files
await session.call_tool(
    "execute_python",
    {
        "code": """
import os

# Create a file
with open('output.txt', 'w') as f:
    f.write('Hello, World!')

# Read it back
with open('output.txt', 'r') as f:
    content = f.read()
    print(f'File content: {content}')

# Clean up
os.remove('output.txt')
"""
    }
)
```

### Data Processing and CSV Export

```python
# Generate and export data
await session.call_tool(
    "execute_python",
    {
        "code": """
import pandas as pd
import numpy as np

# Create sample data
data = {
    'Date': pd.date_range('2024-01-01', periods=10),
    'Sales': np.random.randint(100, 1000, 10),
    'Profit': np.random.randint(50, 500, 10)
}

df = pd.DataFrame(data)

# Save to CSV
df.to_csv('sales_report.csv', index=False)
print(f'Saved {len(df)} rows to sales_report.csv')

# Display summary
print(df.describe())
"""
    }
)
```

## Virtual Environment & Working Directory

The server automatically creates and manages:

### Virtual Environment (`.venv/`)
- **Location**: `./.venv` in the server directory
- **Initialization**: Automatic on first use (via `uv venv`)
- **Package Management**: Uses `uv pip` for fast package installation
- **Package Persistence**: Packages remain installed across executions
- **Isolation**: Separate from system Python installation

### Code Execution Directory (`code_temp/`)
- **Location**: `./code_temp` in the server directory
- **Purpose**: All Python code executes in this directory
- **File Operations**: All files created/read/written by code go here
- **Persistence**: Files persist between executions
- **Auto-created**: Created automatically on first use

## Security Considerations

**Warning**: This server executes arbitrary Python code on your local machine with filesystem access. Only use it in trusted environments.

- Code runs with the same permissions as the user running the server
- Virtual environment provides process isolation only
- No additional sandboxing or security restrictions
- Full access to local filesystem
- Can modify, create, and delete files

## Requirements

- Python 3.11 or higher
- `uv` package manager (for virtual environment and package management)
- Dependencies managed via `pyproject.toml`:
  - STDIO: `mcp`
  - HTTP: `mcp`, `uvicorn`, `starlette`

**Installing uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## Configuration

### Change Virtual Environment or Work Directory Location

Edit the `VirtualEnvironmentManager` initialization in the server code:

```python
# Change virtual environment location
venv_manager = VirtualEnvironmentManager(venv_path="./my_custom_venv")

# Change work directory location
venv_manager = VirtualEnvironmentManager(work_dir="./my_custom_work_dir")

# Change both
venv_manager = VirtualEnvironmentManager(
    venv_path="./my_custom_venv",
    work_dir="./my_custom_work_dir"
)
```

### Change HTTP Port

Edit the `PORT` constant in the HTTP server:

```python
PORT = 8056  # Change to your desired port
```

### Adjust Timeout Values

Modify timeout parameters in the code:

```python
# Package installation timeout (seconds)
venv_manager.install_package(package, timeout=120)

# Code execution timeout (seconds)
venv_manager.execute_code(code, timeout=60)
```

## Troubleshooting

### Virtual Environment Creation Fails

**Issue**: Error creating virtual environment

**Solution**: Ensure `uv` is installed and available in your PATH:
```bash
uv --version
# If not found, install uv:
pip install uv
```

### Package Installation Hangs

**Issue**: Package installation times out

**Solution**: Increase the timeout or check network connectivity:
```python
success, message = venv_manager.install_package(package, timeout=120)
```

### File Permission Errors

**Issue**: Cannot write to filesystem

**Solution**: Ensure the server has write permissions in the working directory, or change the working directory.

### Import Errors After Installation

**Issue**: Packages install but can't be imported

**Solution**: Verify the virtual environment is being used correctly. Check `venv_manager.python_executable` points to the correct Python binary.

## License

This project is part of the MCP Python Code Interpreter collection.
