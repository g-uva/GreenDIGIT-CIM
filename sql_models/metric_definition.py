# sql_models/metric_definition.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from sqlalchemy import Column, Integer, String, TEXT
from sql_models.base import Base

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    id = Column(Integer, primary_key=True, index=True)
    unified_key = Column(String, unique=True, nullable=False)
    tags = Column(TEXT)
    sources = Column(TEXT)
