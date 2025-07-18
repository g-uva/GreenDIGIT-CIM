import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from project_config.postgres_config import Base
from datetime import datetime

class MetricKeyword(Base):
    __tablename__ = "metric_keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    category = Column(String)
    subcategory = Column(String)
    short_key = Column(String)
    confidence = Column(Float, default=0.5)
    source_key = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
