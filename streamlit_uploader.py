import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime

from namespace_mapper_core import parse_and_extract_file_metrics
from project_services.influx_service import write_mapped_metrics
from sql_services.insert_file_upload_log import insert_file_upload_log
from sql_services.insert_metric_definition import insert_metric_definition
from sql_services.insert_datacenter import insert_datacenter
from ingestion_controller.automated_mapper import process_new_raw_metric

st.title("📁 Unified Metric Ingestion")

uploaded_file = st.file_uploader("Upload a JSON, XML, CSV, YAML, or TXT file", type=["json", "xml", "csv", "yaml", "txt"])
datacenter = st.text_input("Enter datacenter name")

if uploaded_file and datacenter:
    st.info("⏳ Processing file...")

    # Save temporarily
    print("🧪 File uploaded. Starting ingestion process...")

    temp_path = os.path.join("temp_upload", uploaded_file.name)
    os.makedirs("temp_upload", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    try:
        st.write("📂 Parsing and mapping metrics...")
        raw_metrics, mapped_metrics = parse_and_extract_file_metrics(temp_path, datacenter)

        st.write(f"🔍 Raw metrics detected: {list(raw_metrics.keys())}")
        new_mapped_metrics = {}
        for raw_key, value in raw_metrics.items():
            st.write(f"🚀 Classifying + mapping: {raw_key}")
            unified_key = process_new_raw_metric(raw_key)
            new_mapped_metrics[unified_key] = value

        timestamp = datetime.utcnow()
        st.write("📈 Storing metrics in InfluxDB...")
        write_mapped_metrics(new_mapped_metrics, timestamp)

        st.write("🧾 Logging upload...")
        insert_datacenter(name=datacenter)
        insert_file_upload_log(
            filename=uploaded_file.name,
            datacenter_id=1,
            uploaded_by="streamlit_user"
        )

        st.write("🗃️ Storing unified metric definitions in PostgreSQL...")
        for unified_key in new_mapped_metrics.keys():
            insert_metric_definition(unified_key=unified_key)

        st.success("✅ File ingested and stored successfully.")

    except Exception as e:
        st.error(f"❌ Ingestion failed: {str(e)}")

    # Clean up
    os.remove(temp_path)
