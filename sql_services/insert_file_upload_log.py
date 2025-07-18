# sql_services/insert_file_upload_log.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.exc import IntegrityError
from project_config.postgres_config import SessionLocal
from sql_models.upload_log import FileUploadLog

def insert_file_upload_log(filename: str, datacenter_id: int, uploaded_by: str = None):
    session = SessionLocal()
    try:
        log = FileUploadLog(
            filename=filename,
            datacenter_id=datacenter_id,
            uploaded_by=uploaded_by
        )
        session.add(log)
        session.commit()
        print(f"✅ File upload log for '{filename}' inserted successfully.")
    except IntegrityError:
        session.rollback()
        print(f"⚠️ Duplicate entry or constraint issue for file '{filename}'.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error inserting file upload log: {e}")
    finally:
        session.close()
