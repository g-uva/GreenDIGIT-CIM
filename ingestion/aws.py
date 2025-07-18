# ingestion/aws.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
from namespace_mapper import map_raw_metric
from project_services.influx_service import write_mapped_metrics

# Simulated AWS metric values (replace with real SDK/API calls)
aws_metrics = {
    "aws.ec2.cpu": 68.5,
    "aws.ec2.memory": 12.3,
    "aws.ec2.network.in": 150.2,
    "aws.ec2.network.out": 120.4
}

def fetch_and_store_aws_metrics():
    timestamp = datetime.datetime.utcnow().isoformat()
    mapped = []

    for raw_key, value in aws_metrics.items():
        unified = map_raw_metric(raw_key, value, datacenter="aws")
        if unified:
            unified["timestamp"] = timestamp
            mapped.append(unified)

    if mapped:
        write_mapped_metrics(mapped)
        print(f"Stored {len(mapped)} AWS metrics to InfluxDB.")
    else:
        print("No AWS metrics matched the mapping registry.")

# Uncomment below to run manually for testing
# fetch_and_store_aws_metrics()
