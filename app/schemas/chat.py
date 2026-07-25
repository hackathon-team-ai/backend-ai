from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[str] = None
    sender: str  # 'user' | 'assistant'
    content: str
    category: Optional[str] = "General"  # Crop selection, Fertilizers, Diseases, Pests, Weather, Irrigation, Harvesting, Organic Farming
    audio_url: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None  # RAG sources if applicable
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Farming Discussion"
    category: Optional[str] = "General"

class ChatSessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    category: str
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    category: Optional[str] = "General"
    use_rag: bool = False
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessage
    suggested_followups: Optional[List[str]] = []
