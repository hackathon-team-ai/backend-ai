from fastapi import APIRouter, Depends, Query
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.weather import WeatherResponse
from app.services.weather_service import weather_service

router = APIRouter()

@router.get("", response_model=WeatherResponse)
async def get_weather(
    state: str = Query("Maharashtra"),
    district: str = Query("Pune"),
    current_user: dict = Depends(get_current_user)
):
    user_state = state or current_user.get("state") or "Maharashtra"
    user_district = district or current_user.get("district") or "Pune"
    return await weather_service.get_weather_data(state=user_state, district=user_district)
