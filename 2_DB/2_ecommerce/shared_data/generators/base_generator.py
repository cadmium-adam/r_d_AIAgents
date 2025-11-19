"""
Base generator class with common functionality.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from faker import Faker


class BaseGenerator:
    """Base class for all data generators."""

    def __init__(self, fake: Faker = None):
        self.fake = fake or Faker()

    def load_existing_json_file(self, filename: str, output_dir: str = None) -> List[Dict[str, Any]]:
        """Load existing JSON file if it exists, return empty list if not."""
        if output_dir is None:
            if os.path.basename(os.getcwd()) == "shared_data":
                output_dir = "."
            else:
                output_dir = "shared_data"

        filepath = os.path.join(output_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"No existing file found at {filepath}, starting with empty data")
            return []
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            print(f"Loaded {len(data)} existing records from {filepath}")
            return data
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error loading {filepath}: {e}. Starting with empty data.")
            return []

    def get_next_id(self, existing_data: List[Dict[str, Any]]) -> int:
        """Get the next available ID from existing data."""
        if not existing_data:
            return 1
        
        # Find the highest existing ID
        max_id = max(item.get('id', 0) for item in existing_data)
        return max_id + 1

    def merge_and_save_json_file(self, new_data: List[Dict[str, Any]], existing_data: List[Dict[str, Any]], filename: str, output_dir: str = None):
        """Merge new data with existing data and save to JSON file."""
        if output_dir is None:
            if os.path.basename(os.getcwd()) == "shared_data":
                output_dir = "."
            else:
                output_dir = "shared_data"

        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # Combine existing and new data
        combined_data = existing_data + new_data
        
        with open(filepath, "w") as f:
            json.dump(combined_data, f, indent=2, default=str)
        
        print(f"Enhanced {filepath}: {len(existing_data)} existing + {len(new_data)} new = {len(combined_data)} total records")
        return filepath

    def save_to_json_file(self, data: List[Dict[str, Any]], filename: str, output_dir: str = None):
        """Save data to JSON file."""
        if output_dir is None:
            if os.path.basename(os.getcwd()) == "shared_data":
                output_dir = "."
            else:
                output_dir = "shared_data"

        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Saved {len(data)} records to {filepath}")
        return filepath

    def generate_metadata(self, data_counts: Dict[str, int], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata for the generated data."""
        return {
            "generated_at": datetime.now().isoformat(),
            "counts": data_counts,
            "generator_config": config,
        }