from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReportRequest(BaseModel):
    campaign_name: str
    endpoints_data: List[Dict[str, Any]]
    
class ReportResponse(BaseModel):
    id: int
    report_id: str
    campaign_name: str
    status: str
    progress: int
    total_records: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
