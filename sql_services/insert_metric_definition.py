# sql_services/insert_metric_definition.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.exc import IntegrityError
from project_config.postgres_config import SessionLocal
from sql_models.metric_definition import MetricDefinition

def insert_metric_definition(unified_key: str, tags: list = None, sources: list = None):
    session = SessionLocal()
    try:
        metric = MetricDefinition(
            unified_key=unified_key,
            tags=tags or [],
            sources=sources or []
        )
        session.add(metric)
        session.commit()
        print(f"✅ Metric definition '{unified_key}' inserted successfully.")
    except IntegrityError:
        session.rollback()
        print(f"⚠️ Metric definition '{unified_key}' already exists.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting metric definition: {e}")
    finally:
        session.close()
