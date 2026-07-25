from pydantic import BaseModel
from typing import List, Optional

class GovernmentScheme(BaseModel):
    id: str
    title: str
    ministry: str
    category: str
    description: str
    eligibility: List[str]
    benefits: List[str]
    required_documents: List[str]
    application_link: str
    is_national: bool = True
    states_applicable: List[str] = ["All"]

class SchemeFilterRequest(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    state: Optional[str] = None
