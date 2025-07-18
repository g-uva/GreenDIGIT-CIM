# sql_services/insert_datacenter.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.exc import IntegrityError
from project_config.postgres_config import SessionLocal
from sql_models.datacenter import Datacenter

def insert_datacenter(name: str, location: str = None, provider: str = None):
    session = SessionLocal()
    try:
        dc = Datacenter(name=name, location=location, provider=provider)
        session.add(dc)
        session.commit()
        print(f"✅ Datacenter '{name}' inserted successfully.")
    except IntegrityError:
        session.rollback()
        print(f"⚠️ Datacenter '{name}' already exists.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting datacenter: {e}")
    finally:
        session.close()
