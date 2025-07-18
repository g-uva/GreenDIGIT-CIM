# namespace_mapper_core.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.structured_parser import parse_structured_file
from parsers.unstructured_parser import parse_unstructured_text
from project_config.metric_mapping import unified_metric_mapping

def extract_metrics(raw_metrics: dict, datacenter: str) -> dict:
    mapped = {}
    for raw_key, value in raw_metrics.items():
        for unified_key, config in unified_metric_mapping.items():
            if raw_key in config.get("sources", []):
                mapped[unified_key] = value
                break
    return mapped

def parse_and_extract_file_metrics(filepath: str, datacenter: str = "naive") -> dict:
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        raw_metrics = parse_unstructured_text(text, datacenter)
    else:
        raw_metrics = parse_structured_file(filepath)

    return raw_metrics, extract_metrics(raw_metrics, datacenter)
