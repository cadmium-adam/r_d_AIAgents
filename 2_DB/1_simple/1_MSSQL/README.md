# Install

https://hub.docker.com/r/microsoft/mssql-server

```bash
docker volume create mssql_data

docker run --name mssql -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Heslo_1234" -v mssql_data:/sql_data -p 1433:1433 -d mcr.microsoft.com/mssql/server:2022-latest
```

username: sa
password: viz docker command

# UI

Windows: MSSQL Management Studio

https://learn.microsoft.com/en-us/ssms/download-sql-server-management-studio-ssms

VSCode: MSSQL extension

https://learn.microsoft.com/en-us/sql/tools/visual-studio-code-extensions/mssql/mssql-extension-visual-studio-code?view=sql-server-ver16

Mac: Azure Data Studio

https://learn.microsoft.com/en-us/azure-data-studio/download-azure-data-studio?view=sql-server-ver16&tabs=win-install%2Cwin-user-install%2Credhat-install%2Cwindows-uninstall%2Credhat-uninstall

To create a **Microsoft SQL Server (MSSQL)** database using Docker and access it via an **ODBC driver**, follow these steps:

# Python code

To make the python script working we need to install the `ODBC` driver first.

## Install ODBC Driver (on host machine)

Depending on your OS:

### **Ubuntu / Debian**

```bash
# Install the Microsoft GPG key and repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Install packages
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18 unixodbc-dev
```

### **macOS (using Homebrew)**

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_AUTO_UPDATE=1 brew install msodbcsql18
```

### **Windows**

Download and install from:
[ODBC Driver for SQL Server – Windows](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

# Run

## Run directly

`uv run main.py` (or alternative files)

## Run indirectly

Create a virtual environment

```bash
uv venv
```

Activate virtual environment

```bash
source .venv/bin/activate
```

Install packages

```bash
uv sync
```

Run script main (or alternative files)

```bash
python main.py
```
