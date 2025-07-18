# ingestion/gcp.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
from namespace_mapper import map_raw_metric
from project_services.influx_service import write_mapped_metrics

# Simulated GCP metric values (replace with real API fetch logic)
gcp_metrics = {
    "gcp.vm.cpu": 72.1,
    "gcp.vm.mem.used": 10.5,
    "gcp.vm.net.rx": 140.3,
    "gcp.vm.net.tx": 110.9
}

def fetch_and_store_gcp_metrics():
    timestamp = datetime.datetime.utcnow().isoformat()
    mapped = []

    for raw_key, value in gcp_metrics.items():
        unified = map_raw_metric(raw_key, value, datacenter="gcp")
        if unified:
            unified["timestamp"] = timestamp
            mapped.append(unified)

    if mapped:
        write_mapped_metrics(mapped)
        print(f"Stored {len(mapped)} GCP metrics to InfluxDB.")
    else:
        print("No GCP metrics matched the mapping registry.")

# Uncomment below to run manually for testing
# fetch_and_store_gcp_metrics()
