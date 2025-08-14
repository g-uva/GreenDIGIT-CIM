# metrics_store.py
# Purpose: create the DB/collection (with index) and provide a single function to store metrics.

import os
import json
from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://metrics-db:27017/")
DB_NAME = os.getenv("METRICS_DB_NAME", "metricsdb")
COLLECTION_NAME = os.getenv("METRICS_COLLECTION", "metrics")

_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]
_col = _db[COLLECTION_NAME]

# Ensure index on publisher_email for fast lookup
_col.create_index([("publisher_email", ASCENDING)], name="ix_publisher_email")

def store_metric(publisher_email: str, body: Any, timestamp_iso: str | None = None) -> Dict[str, Any]:
    """
    Insert one metric document.
    - publisher_email is the identity extracted from JWT (trusted).
    - body is the raw JSON payload from the request (dict/list/etc).
    - timestamp is set server-side (UTC) unless provided.
    Returns a minimal ack with inserted_id and timestamp.
    """
    if timestamp_iso is None:
        timestamp_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "timestamp": timestamp_iso,
        "publisher_email": publisher_email,
        "body": body,  # Mongo stores this as native BSON/JSON (no stringifying required)
    }

    try:
        result = _col.insert_one(doc)
        return {
            "ok": True,
            "id": str(result.inserted_id),
            "timestamp": timestamp_iso,
            "publisher_email": publisher_email,
        }
    except PyMongoError as e:
        return {"ok": False, "error": str(e)}
