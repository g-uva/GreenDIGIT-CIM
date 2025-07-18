# metric_mapping.py

import json
import os

MAPPING_FILE = os.path.join(os.path.dirname(__file__), "metric_mapping.json")

with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    unified_metric_mapping = json.load(f)
