from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas.scheme import GovernmentScheme
from app.services.scheme_service import scheme_service

router = APIRouter()

@router.get("", response_model=List[GovernmentScheme])
async def list_schemes(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    return scheme_service.get_schemes(search=search, category=category)
