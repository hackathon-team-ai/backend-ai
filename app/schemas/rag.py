from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_kb: float
    num_chunks: int
    uploaded_at: datetime
    status: str = "indexed"

class DocumentQueryRequest(BaseModel):
    query: str
    top_k: int = 4

class DocumentSearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    text: str
    score: float
    metadata: Dict[str, Any]

class DocumentQueryResponse(BaseModel):
    answer: str
    sources: List[DocumentSearchResult]
