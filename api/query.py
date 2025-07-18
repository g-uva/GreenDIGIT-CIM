# api/query.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import APIRouter, Query
from project_services.influx_service import query_metrics

router = APIRouter()

@router.get("/")
def query_metrics_api(
    provider: str = Query(default=None),
    metric: str = Query(...),
    from_time: str = Query(...),
    to_time: str = Query(...)
):
    result = query_metrics(provider=provider, metric=metric, from_time=from_time, to_time=to_time)
    return {"results": result}
