import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sql_services.namespace_generator import generate_namespace
from sql_services.insert_mapped_metric import insert_mapped_metric
from utils.mapping_sync import sync_metric_mapping
from project_models.metric_keyword import MetricKeyword
from project_config.postgres_config import SessionLocal
from ingestion_controller.semantic_classifier import classify_by_semantics

def classify_metric(raw_key: str) -> tuple:
    # First: try semantic classifier (standards-based)
    semantic_result = classify_by_semantics(raw_key)
    if semantic_result:
        return semantic_result

    # Second: try keyword DB
    session = SessionLocal()
    try:
        key = raw_key.lower()
        keyword_hit = session.query(MetricKeyword).filter(MetricKeyword.source_key == key).first()
        if keyword_hit:
            return keyword_hit.category, keyword_hit.subcategory, keyword_hit.short_key
        else:
            # fallback guess (basic keyword rules)
            if "cpu" in key:
                guess = ("performance", "cpu", "utilization")
            elif "mem" in key:
                guess = ("performance", "memory", "usage")
            elif "net" in key or "traffic" in key:
                if "out" in key or "tx" in key:
                    guess = ("network", "traffic", "outgoing")
                else:
                    guess = ("network", "traffic", "incoming")
            elif "power" in key and "solar" not in key:
                guess = ("energy", "power", "total")
            elif "solar" in key:
                guess = ("energy", "renewable", "solar")
            elif "disk" in key:
                if "read" in key:
                    guess = ("storage", "disk", "read_io")
                elif "write" in key:
                    guess = ("storage", "disk", "write_io")
                else:
                    guess = ("storage", "disk", "usage")
            elif "temp" in key or "therm" in key:
                guess = ("environment", "temperature", "ambient")
            else:
                guess = ("uncategorized", "unknown", "unknown")

            # Store guessed keyword for learning
            if guess[0] != "uncategorized":
                new_entry = MetricKeyword(
                    keyword=key,
                    category=guess[0],
                    subcategory=guess[1],
                    short_key=guess[2],
                    confidence=0.3,
                    source_key=key
                )
                session.add(new_entry)
                session.commit()

            return guess
    except Exception as e:
        print(f"❌ Error classifying metric: {e}")
        return ("uncategorized", "unknown", "unknown")
    finally:
        session.close()

def process_new_raw_metric(raw_key: str) -> str:
    category, subcategory, metric_short_key = classify_metric(raw_key)

    if category == "uncategorized":
        print(f"⚠️ Unable to classify raw metric: {raw_key}")
        return raw_key

    unified_key = generate_namespace(category, subcategory, metric_short_key)
    tags = list(set([category, subcategory, metric_short_key]))

    # Insert into relational DB
    insert_mapped_metric(
        unified_key=unified_key,
        source_keys=[raw_key],
        tags=tags
    )

    # Sync to JSON file
    sync_metric_mapping(
        unified_key=unified_key,
        source_key=raw_key,
        tags=tags
    )

    return unified_key
