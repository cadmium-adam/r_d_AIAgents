# N8N API

## Prerequisite

Get N8N API KEY - `http://localhost:5678/settings/api`

Save it into `.env` file
ex.

```
N8N_API_KEY=abcd1234
```

## Swagger

`http://localhost:5678/api/v1/docs/`

## Run the scripts

### Enhanced Script (workflow_manager.py) - Recommended

#### Backup Operations

**Backup all workflows**:

```bash
uv run workflow_manager.py backup ./n8n_backup
```

#### Workflow Management

**Delete all workflows**:

```bash
uv run workflow_manager.py delete
```

**Import workflows from folder**:

```bash
uv run workflow_manager.py import ../02_Workflows/01-flow
```

## Backup and Restore Process

### Creating a Workflow Backup

**Backup all workflows**:

```bash
uv run workflow_manager.py backup ./my_n8n_backup_$(date +%Y%m%d)
```

This creates:

- `./my_n8n_backup_YYYYMMDD/` - All workflow JSON files
- `./my_n8n_backup_YYYYMMDD/backup_summary.json` - Backup summary

### Restoring to a New N8N Instance

**Restore workflows**:

```bash
uv run workflow_manager.py import ./my_n8n_backup_YYYYMMDD
```

### Complete Replacement (Delete + Import)

To completely replace all workflows with a backup:

```bash
# Step 1: Delete all existing workflows
uv run workflow_manager.py delete

# Step 2: Import workflows from backup
uv run workflow_manager.py import ./my_n8n_backup_YYYYMMDD
```

⚠️ **Important**: Credentials must be manually recreated in the new N8N instance since the N8N API does not provide credential export functionality.
