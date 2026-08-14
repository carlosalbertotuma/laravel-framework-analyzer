from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from api.database import Base

class ReportJob(Base):
    __tablename__ = "report_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True) # e.g. RPT-2026-000128
    campaign_name = Column(String, index=True)
    status = Column(String, default="PENDING") # PENDING, PROCESSING, COMPLETED, FAILED
    progress = Column(Integer, default=0) # 0 to 100
    total_records = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
