from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SystemAnalytics(BaseModel):
    total_users: int
    active_users: int
    total_chats: int
    disease_scans: int
    documents_indexed: int
    active_tasks: int
    recent_activity: List[Dict[str, Any]]
    chat_category_breakdown: Dict[str, int]
    disease_detection_trends: List[Dict[str, Any]]
