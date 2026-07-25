from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class TaskCreate(BaseModel):
    crop_name: str
    stage: str  # Sowing, Irrigation, Fertilizer, Pest Control, Harvesting
    title: str
    description: Optional[str] = None
    due_date: str # YYYY-MM-DD
    priority: str = "Medium"  # Low, Medium, High

class TaskResponse(BaseModel):
    id: str
    user_id: str
    crop_name: str
    stage: str
    title: str
    description: Optional[str]
    due_date: str
    priority: str
    completed: bool = False
    created_at: datetime
