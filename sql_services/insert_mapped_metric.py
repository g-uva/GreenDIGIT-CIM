import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from sql_models.metric_definition import MetricDefinition
from project_config.postgres_config import SessionLocal

def insert_mapped_metric(unified_key: str, source_keys: list, tags: list):
    session: Session = SessionLocal()
    try:
        # Check if metric already exists
        metric = session.query(MetricDefinition).filter_by(unified_key=unified_key).first()
        if metric:
            metric.sources = list(set((metric.sources or []) + source_keys))
            metric.tags = list(set((metric.tags or []) + tags))
            session.commit()
            print(f"🔁 Updated metric: {unified_key}")
        else:
            new_metric = MetricDefinition(
                unified_key=unified_key,
                sources=source_keys,
                tags=tags
            )
            session.add(new_metric)
            session.commit()
            print(f"✅ Inserted new metric: {unified_key}")

    except Exception as e:
        print(f"❌ Error inserting mapped metric: {e}")
        session.rollback()
    finally:
        session.close()
