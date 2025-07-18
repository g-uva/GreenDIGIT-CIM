# debug/metric_mapper_debugger.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from namespace_mapper_core import extract_metrics
import json

def debug_mapping(raw_metrics: dict, datacenter: str = "naive"):
    print("📥 Raw Input Metrics:")
    for k, v in raw_metrics.items():
        print(f"  - {k}: {v}")

    mapped = extract_metrics(raw_metrics, datacenter)

    print("\n🔁 Mapped Metrics (Unified Keys):")
    for k, v in mapped.items():
        print(f"  - {k}: {v}")

    if not mapped:
        print("\n⚠️ No metrics were mapped. Check if metric_mapping.json contains the correct source keys.")
    return mapped


if __name__ == "__main__":
    # Sample test block (replace with your test content)
    with open("sample_test_data.json", "r", encoding="utf-8") as f:
        raw_metrics = json.load(f)

    debug_mapping(raw_metrics, datacenter="naive")
