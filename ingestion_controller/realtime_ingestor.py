# ingestion_controller/realtime_ingestor.py

from datetime import datetime
from namespace_mapper_core import extract_metrics
from project_services.influx_service import write_mapped_metrics
from sql_services.insert_metric_definition import insert_metric_definition
from sql_services.insert_datacenter import insert_datacenter
from sql_services.insert_file_upload_log import insert_file_upload_log

def ingest_from_api(metric_data: dict, datacenter_name: str, uploaded_by: str = None):
    """
    Ingest real-time metric data from AWS, GCP, or other sources.
    :param metric_data: Raw dictionary of metrics (e.g., from cloud API)
    :param datacenter_name: Name of the cloud/datacenter provider
    :param uploaded_by: Optional user or system identifier
    """
    # Register datacenter if not exists
    insert_datacenter(name=datacenter_name)

    # Apply unified mapping
    mapped_metrics = extract_metrics(metric_data)

    # Write to InfluxDB
    timestamp = datetime.utcnow()
    write_mapped_metrics(mapped_metrics, timestamp)

    # Insert fake file log to simulate source (optional)
    insert_file_upload_log(
        filename=f"API-{datacenter_name}-{timestamp.isoformat()}",
        datacenter_id=1,  # Replace with actual lookup if required
        uploaded_by=uploaded_by
    )

    # Update metric definitions in PostgreSQL if needed
    for unified_key in mapped_metrics:
        insert_metric_definition(unified_key=unified_key)

    print(f"✅ Real-time metrics ingested from {datacenter_name}.")
