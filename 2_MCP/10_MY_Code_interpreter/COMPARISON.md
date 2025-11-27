# MCP Python Code Interpreter - Comparison Guide

## Overview

This project contains two different implementations of a Python code interpreter MCP server:

1. **Container-based** (`stdio/` and `http/` folders at root)
2. **Local with Virtual Environment** (`2_local/` folder)

## Quick Comparison

| Feature | Container (stdio/http) | Local (2_local) |
|---------|----------------------|-----------------|
| **Execution** | Inside Docker container | Local machine with venv |
| **Filesystem Access** | Container filesystem only | Full local filesystem |
| **Package Persistence** | Lost on container restart | Persists in `.venv` |
| **Isolation Level** | Strong (container) | Moderate (venv) |
| **Startup Speed** | Slower (Docker overhead) | Faster (native) |
| **Security** | Sandboxed in container | Runs with user permissions |
| **File Output** | Lost unless volume mounted | Saved to local directory |
| **Setup Complexity** | Requires Docker | Just Python |
| **Resource Usage** | Higher (container overhead) | Lower (native process) |
| **Portability** | High (Docker image) | Requires Python installed |

## Use Cases

### Use Container Version When:

- ✅ You need strong isolation from the host system
- ✅ You're running untrusted or experimental code
- ✅ You want reproducible, portable execution environment
- ✅ You need to deploy the server in production
- ✅ You want easy cleanup (just remove the container)
- ✅ You're testing code that might affect system state

**Example**: Running AI-generated code, public-facing services, CI/CD pipelines

### Use Local Version When:

- ✅ You need to save files permanently on your filesystem
- ✅ You want faster execution (no Docker overhead)
- ✅ You need packages to persist between sessions
- ✅ You're doing development work on your own machine
- ✅ You need to interact with local files/databases
- ✅ You trust the code being executed

**Example**: Data analysis, local development, personal automation scripts

## Architecture Differences

### Container Version (stdio/http)

```
┌─────────────────────────────────────┐
│         Docker Container            │
│  ┌───────────────────────────────┐  │
│  │   MCP Server                  │  │
│  │   - Executes code             │  │
│  │   - pip install               │  │
│  │   - Container filesystem      │  │
│  └───────────────────────────────┘  │
│                                     │
│  Everything lost on restart         │
└─────────────────────────────────────┘
```

### Local Version (2_local)

```
┌─────────────────────────────────────┐
│         Your Machine                │
│  ┌───────────────────────────────┐  │
│  │   MCP Server                  │  │
│  │   - Executes code in venv     │  │
│  │   - pip install to venv       │  │
│  │   - Full filesystem access    │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   .venv/                      │  │
│  │   - Packages persist          │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │   Output Files                │  │
│  │   - *.csv, *.txt, *.png, etc  │  │
│  │   - Persists on disk          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Example Workflows

### Container Version: Quick Experiment

```bash
# Start fresh container
docker run -i mcp-python-stdio

# Run code
echo '{"code": "print(1+1)"}' | # Send to container

# Stop container
docker stop <container_id>

# Everything is gone - clean slate next time
```

### Local Version: Data Analysis Project

```bash
# Start server (first time creates venv)
cd 2_local/stdio
python mcp_python_server.py

# Install packages once
install_dependencies(["pandas", "matplotlib", "seaborn"])

# Run analysis - saves files
execute_python("""
import pandas as pd
df = pd.read_csv('data.csv')
df.to_csv('report.csv')
""")

# Files persist: report.csv saved to disk
# Next time: packages still installed, no reinstall needed
```

## File Persistence Examples

### Container Version

```python
# This file is lost when container stops
execute_python("""
with open('report.txt', 'w') as f:
    f.write('Important data')
""")

# Next container run: file doesn't exist
```

### Local Version

```python
# This file persists on your filesystem
execute_python("""
with open('report.txt', 'w') as f:
    f.write('Important data')
""")

# Next server run: file still exists
# You can also access it from other programs
```

## Package Installation

### Container Version

```python
# Install pandas
install_dependencies(["pandas"])

# Use pandas
execute_python("import pandas as pd; print(pd.__version__)")

# Stop container and restart
# Must install pandas again!
install_dependencies(["pandas"])
```

### Local Version

```python
# Install pandas (first time)
install_dependencies(["pandas"])

# Use pandas
execute_python("import pandas as pd; print(pd.__version__)")

# Stop server and restart
# Pandas is still installed in venv!
execute_python("import pandas as pd; print(pd.__version__)")  # Works immediately
```

## Security Considerations

### Container Version

- ✅ Code runs isolated from host system
- ✅ Limited filesystem access
- ✅ Can't affect host Python installation
- ✅ Resource limits can be set
- ✅ Easy to destroy and recreate

**Risk Level**: Low - Good for untrusted code

### Local Version

- ⚠️ Code runs with your user permissions
- ⚠️ Full filesystem access
- ⚠️ Can read/write any file you can access
- ⚠️ Can execute system commands
- ⚠️ Virtual env provides minimal isolation

**Risk Level**: Medium to High - Only for trusted code

## Migration Between Versions

### From Container to Local

If you want to persist work from container version:

1. Extract files from container before stopping:
   ```bash
   docker cp <container_id>:/app/output.csv ./output.csv
   ```

2. Export installed packages:
   ```bash
   docker exec <container_id> pip list --format=freeze > requirements.txt
   ```

3. Use local version and reinstall:
   ```bash
   cd 2_local/stdio
   pip install -r requirements.txt
   ```

### From Local to Container

If you want to containerize local work:

1. Your files are already on disk (no extraction needed)

2. Create requirements.txt from venv:
   ```bash
   cd 2_local/stdio/.venv
   pip list --format=freeze > requirements.txt
   ```

3. Build custom Docker image:
   ```dockerfile
   FROM python:3.11-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   # ... rest of Dockerfile
   ```

## Recommendations

### For Production/Public Services
→ Use **Container Version** (stdio/http)

### For Personal Development
→ Use **Local Version** (2_local)

### For Data Science/Analysis
→ Use **Local Version** (2_local) - Files persist

### For Testing Untrusted Code
→ Use **Container Version** (stdio/http) - Better isolation

### For CI/CD Pipelines
→ Use **Container Version** (stdio/http) - Reproducible

### For Quick Scripts
→ Use **Local Version** (2_local) - Faster startup

## Both Versions Support

- ✅ STDIO transport (for CLI integration)
- ✅ HTTP transport (for web services)
- ✅ Package installation via pip
- ✅ Python code execution
- ✅ Comprehensive test suites
- ✅ Error handling and timeouts
- ✅ MCP standard compliance

## Choose Based On Your Needs

**Need isolation?** → Container
**Need persistence?** → Local
**Need both?** → Use local for development, deploy with container
