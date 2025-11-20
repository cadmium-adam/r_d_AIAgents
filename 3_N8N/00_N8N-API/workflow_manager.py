#!/usr/bin/env python3
"""
N8N Workflow Manager Script

This script provides functionality to:
1. Remove all workflows from N8N
2. Import all workflows from a specified folder
3. Export/backup all workflows from N8N

Usage:
    python workflow_manager.py delete
    python workflow_manager.py import <folder_path>
    python workflow_manager.py backup <backup_folder>

Requirements:
    - N8N API Key set in .env file or N8N_API_KEY environment variable
    - N8N instance running on http://localhost:5678 (or set N8N_BASE_URL)

Note: Credential backup is not supported by N8N API
"""

import requests
import json
import sys
import os
import glob
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class N8NWorkflowManager:
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize N8N API client

        Args:
            base_url: Your n8n instance URL (defaults to http://localhost:5678)
            api_key: API key for authentication (gets from env if not provided)
        """
        self.base_url = (
            base_url or os.getenv("N8N_BASE_URL", "http://localhost:5678")
        ).rstrip("/")
        self.api_key = api_key or os.getenv("N8N_API_KEY")

        if not self.api_key:
            raise ValueError(
                "N8N_API_KEY must be provided or set in environment variables"
            )

        self.session = requests.Session()
        self.session.headers.update({"X-N8N-API-KEY": self.api_key})

        # Test connection
        self._test_connection()

    def _test_connection(self) -> None:
        """Test connection to N8N API"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows?limit=1")
            if response.status_code == 401:
                raise Exception("Authentication failed - check your API key")
            elif response.status_code != 200:
                raise Exception(
                    f"Failed to connect to N8N (HTTP {response.status_code})"
                )
            print(f"✓ Connected to N8N at {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to N8N: {e}")

    def get_all_workflows(self) -> List[Dict]:
        """Fetch all workflows from n8n with pagination"""
        all_workflows = []
        cursor = None

        while True:
            # Build URL with pagination
            url = f"{self.base_url}/api/v1/workflows"
            params = {"limit": 100}  # Get 100 at a time
            if cursor:
                params["cursor"] = cursor

            response = self.session.get(url, params=params)
            if response.status_code != 200:
                raise Exception(
                    f"Failed to fetch workflows: {response.status_code} - {response.text}"
                )

            data = response.json()

            # Handle both array response and paginated response
            if isinstance(data, list):
                # Old API format - just return the list
                return data
            elif isinstance(data, dict):
                # New API format with pagination or different structure
                if "data" in data:
                    workflows = data.get("data", [])
                    all_workflows.extend(workflows)

                    # Check if there are more pages
                    next_cursor = data.get("nextCursor")
                    if not next_cursor:
                        break
                    cursor = next_cursor
                else:
                    # Maybe the workflows are directly in the dict response
                    # Check if it looks like pagination metadata
                    if any(key in data for key in ["count", "total", "workflows"]):
                        workflows = data.get("workflows", data.get("data", []))
                        all_workflows.extend(workflows)
                        break
                    else:
                        # Unknown format, return what we have
                        return []
            else:
                # Fallback - try to get data as array
                all_workflows = data if isinstance(data, list) else []
                break

        return all_workflows

    def get_workflow_by_id(self, workflow_id: str) -> Dict:
        """Get a single workflow by ID with full details"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"

        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch workflow {workflow_id}: {response.status_code} - {response.text}"
            )

        return response.json()

    def export_all_workflows(self, export_folder: str) -> Dict:
        """Export all workflows to a folder"""
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
            print(f"Created export folder: {export_folder}")

        workflows = self.get_all_workflows()

        if not workflows:
            print("No workflows found to export")
            return {"total": 0, "exported": 0, "failed": 0, "results": []}

        print(f"Exporting {len(workflows)} workflows to {export_folder}...")

        exported_count = 0
        failed_count = 0
        results = []

        for workflow in workflows:
            workflow_id = workflow.get("id")
            workflow_name = workflow.get("name", "Unknown")

            try:
                # Get full workflow details
                full_workflow = self.get_workflow_by_id(workflow_id)

                # Create a safe filename
                safe_name = "".join(
                    c if c.isalnum() or c in (" ", "-", "_") else "_"
                    for c in workflow_name
                )
                safe_name = safe_name.replace(" ", "_").strip("_")
                filename = f"{safe_name}_{workflow_id}.json"
                filepath = os.path.join(export_folder, filename)

                # Save workflow to file
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(full_workflow, f, indent=2, ensure_ascii=False)

                print(f"✓ Exported: {workflow_name} -> {filename}")
                exported_count += 1

                results.append(
                    {
                        "workflow_name": workflow_name,
                        "workflow_id": workflow_id,
                        "filename": filename,
                        "success": True,
                    }
                )

            except Exception as e:
                print(f"✗ Failed to export {workflow_name}: {e}")
                failed_count += 1

                results.append(
                    {
                        "workflow_name": workflow_name,
                        "workflow_id": workflow_id,
                        "success": False,
                        "error": str(e),
                    }
                )

        # Summary
        print(f"\n{'='*50}")
        print("Export Summary:")
        print(f"  Total workflows: {len(workflows)}")
        print(f"  Successfully exported: {exported_count}")
        if failed_count > 0:
            print(f"  Failed: {failed_count}")
        print(f"  Export folder: {export_folder}")
        print(f"{'='*50}")

        return {
            "total": len(workflows),
            "exported": exported_count,
            "failed": failed_count,
            "results": results,
        }

    def backup_all_workflows(self, backup_folder: str) -> Dict:
        """Backup all workflows to a folder"""
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
            print(f"Created backup folder: {backup_folder}")

        print("Starting N8N workflow backup...")
        print("=" * 50)

        # Export workflows directly to backup folder (no subfolder needed)
        workflow_result = self.export_all_workflows(backup_folder)

        # Create a backup summary
        summary_path = os.path.join(backup_folder, "backup_summary.json")
        backup_summary = {
            "backup_date": "auto-generated",
            "n8n_instance": self.base_url,
            "workflows": workflow_result,
            "total_items": workflow_result["total"],
            "successfully_backed_up": workflow_result["exported"],
        }

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(backup_summary, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*50}")
        print("WORKFLOW BACKUP SUMMARY:")
        print(
            f"  Workflows: {workflow_result['exported']}/{workflow_result['total']} exported"
        )
        print(f"  Backup folder: {backup_folder}")
        print(f"  Summary file: backup_summary.json")
        print(f"{'='*50}")

        return backup_summary

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a single workflow by ID"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"

        response = self.session.delete(url)
        return response.status_code == 200

    def delete_all_workflows(self, confirm: bool = False) -> Dict:
        """Delete all workflows"""
        workflows = self.get_all_workflows()

        if not workflows:
            print("No workflows found to delete")
            return {"total": 0, "deleted": 0, "failed": 0}

        if not confirm:
            print(f"\nFound {len(workflows)} workflows:")
            # Show first 10 workflows safely
            workflows_to_show = workflows[:10] if len(workflows) > 10 else workflows
            for workflow in workflows_to_show:
                workflow_name = workflow.get("name", "Unknown")
                workflow_id = workflow.get("id", "Unknown")
                print(f"  - {workflow_name} (ID: {workflow_id})")
            if len(workflows) > 10:
                print(f"  ... and {len(workflows) - 10} more")

            user_input = input(
                f"\nAre you sure you want to delete ALL {len(workflows)} workflows? This cannot be undone! (yes/no): "
            )
            if user_input.lower() not in ["yes", "y"]:
                print("Operation cancelled")
                return {"total": len(workflows), "deleted": 0, "failed": 0}

        deleted_count = 0
        failed_count = 0

        print(f"\nDeleting {len(workflows)} workflows...")
        for workflow in workflows:
            workflow_id = workflow["id"]
            workflow_name = workflow["name"]

            if self.delete_workflow(workflow_id):
                deleted_count += 1
                print(f"✓ Deleted: {workflow_name} (ID: {workflow_id})")
            else:
                failed_count += 1
                print(f"✗ Failed to delete: {workflow_name} (ID: {workflow_id})")

        result = {
            "total": len(workflows),
            "deleted": deleted_count,
            "failed": failed_count,
        }

        print(f"\nDeletion complete:")
        print(f"  Total workflows: {result['total']}")
        print(f"  Successfully deleted: {result['deleted']}")
        if result["failed"] > 0:
            print(f"  Failed to delete: {result['failed']}")

        return result

    def clean_workflow_json(self, workflow_data: Dict) -> Dict:
        """Clean workflow JSON for import by removing problematic fields"""
        cleaned = {
            "name": workflow_data.get("name", "Imported Workflow"),
            "nodes": [],
            "connections": workflow_data.get("connections", {}),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData", {}),
        }

        # Clean nodes by removing IDs
        for node in workflow_data.get("nodes", []):
            cleaned_node = dict(node)
            if "id" in cleaned_node:
                del cleaned_node["id"]
            cleaned["nodes"].append(cleaned_node)

        return cleaned

    def validate_workflow_file(self, file_path: str) -> bool:
        """Validate that a file contains valid JSON workflow data"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Basic validation - must have name and nodes
            if not isinstance(data, dict):
                return False
            if "name" not in data and "nodes" not in data:
                return False

            return True
        except (json.JSONDecodeError, IOError):
            return False

    def import_workflow(self, workflow_data: Dict) -> Dict:
        """Import a single workflow"""
        url = f"{self.base_url}/api/v1/workflows"

        # Clean the workflow data
        cleaned_data = self.clean_workflow_json(workflow_data)

        response = self.session.post(url, json=cleaned_data)
        return {
            "status_code": response.status_code,
            "success": response.status_code in [200, 201],
            "response": (
                response.json() if response.status_code in [200, 201] else response.text
            ),
            "workflow_name": cleaned_data["name"],
        }

    def import_workflows_from_folder(self, folder_path: str) -> Dict:
        """Import all JSON workflow files from a folder and its subfolders recursively"""
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder '{folder_path}' does not exist")

        # Find all JSON files recursively in folder and subfolders
        json_files = glob.glob(
            os.path.join(folder_path, "**", "*.json"), recursive=True
        )

        if not json_files:
            print(f"No JSON files found in {folder_path} or its subfolders")
            return {"total": 0, "success": 0, "failed": 0, "results": []}

        print(
            f"Found {len(json_files)} JSON file(s) to process (searching recursively)"
        )

        results = []
        success_count = 0
        failed_count = 0

        for file_path in sorted(json_files):
            filename = os.path.basename(file_path)
            # Show relative path from the base folder for better context
            relative_path = os.path.relpath(file_path, folder_path)
            print(f"\nProcessing: {relative_path}")

            # Validate file
            if not self.validate_workflow_file(file_path):
                print(f"✗ Invalid JSON or workflow format: {relative_path}")
                failed_count += 1
                results.append(
                    {
                        "file": relative_path,
                        "success": False,
                        "error": "Invalid JSON or workflow format",
                    }
                )
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)

                workflow_name = workflow_data.get("name", filename.replace(".json", ""))

                # Import the workflow
                result = self.import_workflow(workflow_data)

                if result["success"]:
                    print(f"✓ Successfully imported: {result['workflow_name']}")
                    if (
                        isinstance(result["response"], dict)
                        and "id" in result["response"]
                    ):
                        print(f"  Workflow ID: {result['response']['id']}")
                    success_count += 1
                else:
                    print(f"✗ Failed to import: {result['workflow_name']}")
                    print(f"  Error ({result['status_code']}): {result['response']}")
                    failed_count += 1

                results.append(
                    {
                        "file": relative_path,
                        "workflow_name": result["workflow_name"],
                        "success": result["success"],
                        "status_code": result["status_code"],
                        "response": result["response"],
                    }
                )

            except Exception as e:
                print(f"✗ Error processing {relative_path}: {e}")
                failed_count += 1
                results.append(
                    {"file": relative_path, "success": False, "error": str(e)}
                )

        # Summary
        print(f"\n{'='*50}")
        print("Import Summary:")
        print(f"  Total files: {len(json_files)}")
        print(f"  Successfully processed: {success_count}")
        if failed_count > 0:
            print(f"  Failed: {failed_count}")
        print(f"{'='*50}")

        return {
            "total": len(json_files),
            "success": success_count,
            "failed": failed_count,
            "results": results,
        }


def show_usage():
    """Show usage information"""
    print("N8N Workflow Manager")
    print("===================")
    print()
    print("This script can manage N8N workflows: delete, import, and backup.")
    print()
    print("Usage:")
    print("  Workflow Operations:")
    print(
        "    python workflow_manager.py delete                          - Delete all workflows"
    )
    print(
        "    python workflow_manager.py import <folder_path>            - Import workflows from folder"
    )
    print()
    print("  Backup Operations:")
    print(
        "    python workflow_manager.py backup <backup_folder>          - Backup all workflows"
    )
    print()
    print("Configuration:")
    print("  Set environment variables or create .env file:")
    print("  - N8N_API_KEY: Your n8n API key (required)")
    print(
        "  - N8N_BASE_URL: Your n8n instance URL (optional, defaults to http://localhost:5678)"
    )
    print()
    print("Examples:")
    print("  python workflow_manager.py backup ./n8n_backup")
    print("  python workflow_manager.py import ../02_Workflows/01-flow")
    print("  python workflow_manager.py delete")
    print()
    print(
        "Note: Credential backup is not supported by N8N API - manual documentation required."
    )
    print()


def main():
    # Parse command line arguments
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        show_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    try:
        # Initialize the workflow manager
        manager = N8NWorkflowManager()

        if command == "delete":
            result = manager.delete_all_workflows()

        elif command == "import":
            if len(sys.argv) < 3:
                print("Error: Folder path required for import command")
                print("Usage: python workflow_manager.py import <folder_path>")
                sys.exit(1)

            folder_path = sys.argv[2]
            result = manager.import_workflows_from_folder(folder_path)

        elif command == "backup":
            if len(sys.argv) < 3:
                print("Error: Backup folder path required for backup command")
                print("Usage: python workflow_manager.py backup <backup_folder>")
                sys.exit(1)

            backup_folder = sys.argv[2]
            result = manager.backup_all_workflows(backup_folder)

        else:
            print(f"Unknown command: {command}")
            show_usage()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
