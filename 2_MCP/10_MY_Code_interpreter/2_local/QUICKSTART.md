# Quick Start Guide - Local Python Code Interpreter

## What's Different?

This runs Python code **locally** using a **virtual environment managed by uv**:

- ✅ Packages persist between runs (saved in `.venv`)
- ✅ Full filesystem access
- ✅ Faster startup (no Docker overhead)
- ✅ Blazing-fast package installation via `uv`
- ✅ Files saved directly to your local filesystem
- ⚠️ Code runs with your user permissions

## Quick Test - STDIO Version

```bash
# Terminal 1: Setup and run the server
cd 2_local/stdio
uv venv && source .venv/bin/activate
uv sync
python mcp_python_server.py

# Terminal 2: Run the test
cd 2_local/stdio/test
uv venv && source .venv/bin/activate
uv sync
python main.py quick
```

## Quick Test - HTTP Version

```bash
# Terminal 1: Setup and run the server
cd 2_local/http
uv venv && source .venv/bin/activate
uv sync
python mcp_python_server.py

# Terminal 2: Run the test
cd 2_local/http/test
uv venv && source .venv/bin/activate
uv sync
python main.py quick
```

## Example: Data Analysis Workflow

```python
# Install data science packages (one time)
await session.call_tool(
    "install_dependencies",
    {"packages": ["pandas", "matplotlib", "seaborn"]}
)

# Run analysis and save results
await session.call_tool(
    "execute_python",
    {
        "code": """
import pandas as pd
import matplotlib.pyplot as plt

# Create sample data
data = {'Product': ['A', 'B', 'C'], 'Sales': [100, 150, 120]}
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('report.csv', index=False)

# Create visualization
plt.bar(df['Product'], df['Sales'])
plt.savefig('sales_chart.png')

print('✓ Generated report.csv and sales_chart.png')
"""
    }
)
```

## Run All Tests

```bash
# STDIO version
cd 2_local/stdio/test
uv venv && source .venv/bin/activate
uv sync
python main.py

# HTTP version
cd 2_local/http/test
uv venv && source .venv/bin/activate
uv sync
python main.py
```

## Where Files Are Saved

Files created by your code are saved in the **`code_temp/` directory**:

```bash
2_local/stdio/    # or 2_local/http/
├── .venv/        # Virtual environment (auto-created)
└── code_temp/    # Working directory (auto-created)
    ├── *.py      # Your script outputs
    ├── *.csv     # Data files
    ├── *.txt     # Text files
    └── *.png     # Images
```

**All file operations in your Python code happen in `code_temp/`**

## Customizing Directories

Both the virtual environment and work directory can be customized:

```python
# In mcp_python_server.py
venv_manager = VirtualEnvironmentManager(
    venv_path="./my_venv",      # Custom venv location
    work_dir="./my_work_dir"    # Custom work directory
)
```

## Key Features

### Package Persistence
```bash
# First run: Install packages
install_dependencies(["pandas", "numpy"])

# Stop server, restart

# Second run: Packages already installed!
execute_python("import pandas; print(pandas.__version__)")  # Works immediately
```

### File Persistence
```bash
# Run 1: Save data (saved to code_temp/)
execute_python("""
import pandas as pd
df = pd.DataFrame({'a': [1,2,3]})
df.to_csv('data.csv')  # Saved to code_temp/data.csv
""")

# Stop server

# Run 2: Load data (from code_temp/)
execute_python("""
import pandas as pd
df = pd.read_csv('data.csv')  # Reads from code_temp/data.csv
print(df)
""")  # File still exists in code_temp/!
```

## Simple Usage

### STDIO (for command-line integration)
```bash
cd 2_local/stdio
uv venv && source .venv/bin/activate
uv sync
python mcp_python_server.py
```

### HTTP (for web services/APIs)
```bash
cd 2_local/http
uv venv && source .venv/bin/activate
uv sync
python mcp_python_server.py
# Server runs on http://localhost:8056
```

## Requirements

- Python 3.11+
- `uv` package manager (installs packages 10-100x faster than pip!)
- Dependencies in `pyproject.toml`

**Install uv:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```
