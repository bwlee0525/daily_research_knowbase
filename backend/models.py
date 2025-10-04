from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, List

class ReportRequest(BaseModel):
    topic: str
    tags: List[str] = []
    template: str = "report_v1"
    data: Dict[str, Any] = {}   # 可傳 subtitle/sections 等欄位

class ReportMeta(BaseModel):
    report_id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
