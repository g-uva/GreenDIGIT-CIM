# project_services/influx_service.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
from project_config.config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_mapped_metrics(mapped_metrics: dict, timestamp: datetime = None):
    """
    Write mapped metric key-value pairs to InfluxDB with an optional timestamp.
    """
    if timestamp is None:
        timestamp = datetime.utcnow()

    points = []
    for key, value in mapped_metrics.items():
        point = (
            Point("metric")
            .tag("unified_key", key)
            .field("value", float(value))
            .time(timestamp, WritePrecision.NS)
        )
        points.append(point)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
    print("✅ Metrics written to InfluxDB.")
