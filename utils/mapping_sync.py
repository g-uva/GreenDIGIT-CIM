# utils/mapping_sync.py
import os
import json

MAPPING_PATH = os.path.join(os.path.dirname(__file__), "../metric_mapping.json")

def sync_metric_mapping(unified_key: str, source_key: str, tags: list = None):
    """
    Adds or updates the mapping file with the new source under the unified key.
    """
    if tags is None:
        tags = []

    # Load current mapping
    if os.path.exists(MAPPING_PATH):
        with open(MAPPING_PATH, "r", encoding="utf-8") as f:
            mapping = json.load(f)
    else:
        mapping = {}

    # Add or update the unified key
    if unified_key not in mapping:
        mapping[unified_key] = {
            "tags": tags,
            "sources": [source_key]
        }
    else:
        if source_key not in mapping[unified_key]["sources"]:
            mapping[unified_key]["sources"].append(source_key)
        for tag in tags:
            if tag not in mapping[unified_key]["tags"]:
                mapping[unified_key]["tags"].append(tag)

    # Write back
    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    print(f"🔄 Synced metric_mapping.json with key: {unified_key}")
