# metrics_store.py
# Purpose: create the DB/collection (with index) and provide a single function to store metrics.

import os, json, zlib
from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
from pymongo.write_concern import WriteConcern

MONGO_URI = os.getenv("MONGO_URI", "mongodb://metrics-db:27017/")
DB_NAME = os.getenv("METRICS_DB_NAME", "metricsdb")
COLLECTION_NAME = os.getenv("METRICS_COLLECTION", "metrics")
INGEST_SESSIONS = "ingest_sessions"

# For bulk idempotency resume (in case of network blip, 502, etc.)
_sess = _db[INGEST_SESSIONS]
_sess.create_index(
    [("publisher_email", ASCENDING), ("idempotency_key", ASCENDING), ("seq", ASCENDING)],
    name="uq_pub_batch_seq", unique=True
)

_client = MongoClient(MONGO_URI)
_db = _client[DB_NAME]
_col = _db[COLLECTION_NAME]

# Ensure index on publisher_email for fast lookup
def ensure_indexes():
    _col.create_index([("timestamp", ASCENDING)], name="ix_timestamp")
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
    

@app.post("/submit/ndjson", tags=["Metrics"], summary="Stream NDJSON (optionally gzip)")
async def submit_ndjson(request: Request, publisher_email: str = Depends(verify_token)):
    # Gzip support
    content_encoding = (request.headers.get("Content-Encoding") or "").lower()
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS) if content_encoding == "gzip" else None

    # Majority+journal write concern for integrity (tune later if needed)
    col = _db.get_collection(_col.name, write_concern=WriteConcern(w="majority", j=True))

    buf = b""
    ops, inserted = [], 0

    async for chunk in request.stream():
        if decoder:
            chunk = decoder.decompress(chunk)
        buf += chunk
        *lines, buf = buf.split(b"\n")
        for line in lines:
            if not line.strip():
                continue
            body = json.loads(line)
            ops.append(InsertOne({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "publisher_email": publisher_email,
                "body": body
            }))
            if len(ops) >= BULK_MAX_OPS:
                col.bulk_write(ops, ordered=False, bypass_document_validation=True)
                inserted += len(ops)
                ops = []

    # flush decoder tail & last line(s)
    if decoder:
        tail = decoder.flush()
        if tail:
            buf += tail
    for line in filter(None, buf.split(b"\n")):
        if line.strip():
            body = json.loads(line)
            ops.append(InsertOne({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "publisher_email": publisher_email,
                "body": body
            }))
    if ops:
        col.bulk_write(ops, ordered=False, bypass_document_validation=True)
        inserted += len(ops)

    return {"ok": True, "inserted": inserted}

def store_metrics_bulk(publisher_email: str, bodies: list[dict], ts_iso: str | None = None) -> dict:
    if ts_iso is None:
        ts_iso = datetime.now(timezone.utc).isoformat()
    ops = [InsertOne({"timestamp": ts_iso, "publisher_email": publisher_email, "body": b}) for b in bodies]
    try:
        col = _db.get_collection(COLLECTION_NAME, write_concern=WriteConcern(w="majority", j=True))
        res = col.bulk_write(ops, ordered=False, bypass_document_validation=True)
        return {"ok": True, "inserted": res.inserted_count}
    except PyMongoError as e:
        return {"ok": False, "error": str(e)}

# Must initialise the indexes.
ensure_indexes()