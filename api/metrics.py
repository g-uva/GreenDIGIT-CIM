# api/metrics.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Query
from ingestion.aws import fetch_and_store_aws_metrics
from ingestion.gcp import fetch_and_store_gcp_metrics

router = APIRouter()

@router.get("/")
def fetch_metrics(provider: str = Query(..., enum=["aws", "gcp"])):
    if provider == "aws":
        fetch_and_store_aws_metrics()
        return {"message": "AWS metrics fetched and stored."}
    elif provider == "gcp":
        fetch_and_store_gcp_metrics()
        return {"message": "GCP metrics fetched and stored."}
    return {"message": "Provider not recognized."}
