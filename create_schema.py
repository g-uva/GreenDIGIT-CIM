# create_schema.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project_config.postgres_config import engine
from sql_models.base import Base
from sql_models.datacenter import Datacenter
from sql_models.metric_definition import MetricDefinition
from sql_models.upload_log import FileUploadLog

def create_all_tables():
    print("Creating all tables in the database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_all_tables()
