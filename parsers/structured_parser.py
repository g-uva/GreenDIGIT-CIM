# parsers/structured_parser.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import yaml
import csv
import xml.etree.ElementTree as ET
from collections.abc import MutableMapping

def flatten_dict(d, parent_key='', sep='.') -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def parse_structured_file(filepath: str) -> dict:
    ext = os.path.splitext(filepath)[-1].lower()

    if ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return flatten_dict(data)

    elif ext == ".yaml":
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return flatten_dict(data)

    elif ext == ".csv":
        result = {}
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                for key, value in row.items():
                    flat_key = f"row{i}.{key.strip()}"
                    try:
                        result[flat_key] = float(value)
                    except:
                        continue
        return result

    elif ext == ".xml":
        tree = ET.parse(filepath)
        root = tree.getroot()
        result = {}

        def recurse_xml(elem, parent=""):
            for child in elem:
                key = f"{parent}.{child.tag}" if parent else child.tag
                if list(child):
                    recurse_xml(child, key)
                else:
                    try:
                        result[key] = float(child.text)
                    except:
                        continue

        recurse_xml(root)
        return result

    else:
        raise ValueError(f"Unsupported structured file type: {ext}")
