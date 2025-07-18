# sql_models/upload_log.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sql_models.base import Base

class FileUploadLog(Base):
    __tablename__ = "file_upload_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    datacenter_id = Column(Integer, ForeignKey("datacenters.id"))
    uploaded_by = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
