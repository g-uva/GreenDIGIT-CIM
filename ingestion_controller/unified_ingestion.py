# ingestion_controller/unified_ingestion.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from namespace_mapper_core import parse_and_extract_file_metrics
from project_services.influx_service import write_mapped_metrics
from sql_services.insert_file_upload_log import insert_file_upload_log
from sql_services.insert_metric_definition import insert_metric_definition
from sql_services.insert_datacenter import insert_datacenter
from ingestion_controller.automated_mapper import process_new_raw_metric
from datetime import datetime

SUPPORTED_FILE_TYPES = [".json", ".xml", ".csv", ".yaml", ".txt"]

def ingest_from_file(file_path: str, datacenter_name: str, uploaded_by: str = None):
    ext = os.path.splitext(file_path)[-1].lower()

    if ext not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {ext}")

    # Ensure datacenter is registered
    insert_datacenter(name=datacenter_name)

    # Parse and map metrics automatically
    print("📂 Parsed file, now mapping metrics...")
    raw_metrics, mapped_metrics = parse_and_extract_file_metrics(file_path, datacenter_name)
    print(f"🔍 Raw metrics: {list(raw_metrics.keys())}")
    new_mapped_metrics = {}
    for raw_key, value in raw_metrics.items():
        st.write(f"🚀 Classifying + mapping: {raw_key}")
        unified_key = process_new_raw_metric(raw_key)
        new_mapped_metrics[unified_key] = value

    # Write to InfluxDB
    timestamp = datetime.utcnow()
    print("📈 Writing to InfluxDB...")
    write_mapped_metrics(new_mapped_metrics, timestamp)

    # Insert upload log (datacenter assumed to have ID 1 here)
    insert_file_upload_log(
        filename=os.path.basename(file_path),
        datacenter_id=1,  # Replace with actual lookup logic
        uploaded_by=uploaded_by
    )

    # Optional: update metric definitions in PostgreSQL
    for unified_key, value in new_mapped_metrics.items():
        insert_metric_definition(unified_key=unified_key)

    print("✅ Ingestion complete.")
