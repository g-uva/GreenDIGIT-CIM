# sql_models/datacenter.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Column, Integer, String
from sql_models.base import Base

class Datacenter(Base):
    __tablename__ = "datacenters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=True)
    provider = Column(String, nullable=True)
