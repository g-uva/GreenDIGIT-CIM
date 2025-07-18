# namespace_mapper.py

import json
import csv
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional

# Path to your mapping registry file
MAPPING_FILE = Path("project_config/metric_mapping.json")


def load_mapping_registry() -> Dict[str, Any]:
    with open(MAPPING_FILE, "r") as f:
        return json.load(f)


def build_inverse_mapping(mapping: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    inverse = {}
    for unified_key, data in mapping.items():
        sources = data.get("sources", [])
        tags = data.get("tags", [])
        for src in sources:
            inverse[src] = {"unified_key": unified_key, "tags": tags}
    return inverse


def map_raw_metric(raw_key: str, value: Any, datacenter: str) -> Optional[Dict[str, Any]]:
    mapping = load_mapping_registry()
    inverse_mapping = build_inverse_mapping(mapping)
    if raw_key in inverse_mapping:
        return {
            "unified_key": inverse_mapping[raw_key]["unified_key"],
            "value": try_cast(value),
            "datacenter": datacenter,
            "source_key": raw_key,
            "tags": inverse_mapping[raw_key]["tags"]
        }
    return None


def flatten_json(obj: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_json(v, new_key, sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}"
            items.update(flatten_json(v, new_key, sep))
    else:
        items[parent_key] = obj
    return items


def flatten_xml(elem: ET.Element, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items = {}
    tag = f"{parent_key}{sep}{elem.tag}" if parent_key else elem.tag
    if elem.text and elem.text.strip():
        items[tag] = elem.text.strip()
    for child in elem:
        items.update(flatten_xml(child, tag, sep))
    return items


def flatten_csv(file_path: str, sep: str = ".") -> Dict[str, Any]:
    items = {}
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            for key, value in row.items():
                items[f"row{i}{sep}{key}"] = value
    return items


def flatten_yaml(file_path: str, sep: str = ".") -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    return flatten_json(data, sep=sep)


def detect_format(file_path: str) -> str:
    if file_path.endswith(".json"):
        return "json"
    elif file_path.endswith(".xml"):
        return "xml"
    elif file_path.endswith(".csv"):
        return "csv"
    elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
        return "yaml"
    else:
        raise ValueError("Unsupported file type. Supported formats: .json, .xml, .csv, .yaml")


def extract_metrics(file_path: str, datacenter: str, sep: str = ".") -> List[Dict[str, Any]]:
    format_type = detect_format(file_path)

    if format_type == "json":
        with open(file_path, "r") as f:
            raw_data = json.load(f)
        flat_data = flatten_json(raw_data, sep=sep)
    elif format_type == "xml":
        tree = ET.parse(file_path)
        root = tree.getroot()
        flat_data = flatten_xml(root, sep=sep)
    elif format_type == "csv":
        flat_data = flatten_csv(file_path, sep=sep)
    elif format_type == "yaml":
        flat_data = flatten_yaml(file_path, sep=sep)
    else:
        raise ValueError("Unsupported format")

    result = []
    for raw_key, value in flat_data.items():
        mapped = map_raw_metric(raw_key, value, datacenter)
        if mapped:
            result.append(mapped)

    return result


def try_cast(val: Any):
    try:
        if isinstance(val, str) and "." in val:
            return float(val)
        elif isinstance(val, str):
            return int(val)
        return val
    except Exception:
        return val
