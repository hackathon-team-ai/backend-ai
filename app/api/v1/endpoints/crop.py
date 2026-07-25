from fastapi import APIRouter, Depends
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.crop import CropRecommendationInput, CropRecommendationResponse
from app.services.crop_service import crop_service

router = APIRouter()

@router.post("/recommend", response_model=CropRecommendationResponse)
async def recommend_crops(
    req: CropRecommendationInput,
    current_user: dict = Depends(get_current_user)
):
    return crop_service.recommend_crops(req)
