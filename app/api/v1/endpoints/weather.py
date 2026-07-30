from fastapi import APIRouter, Depends, Query
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.weather import WeatherResponse
from app.services.weather_service import weather_service

router = APIRouter()

@router.get("", response_model=WeatherResponse)
async def get_weather(
    state: str = Query(None),
    district: str = Query(None),
    current_user: dict = Depends(get_current_user)
):
    # Priority: query param > user profile > default
    # If district is explicitly passed in query, use it; otherwise use user's profile district
    user_state = state if state is not None else (current_user.get("state") or "Maharashtra")
    user_district = district if district is not None else (current_user.get("district") or "Pune")
    return await weather_service.get_weather_data(state=user_state, district=user_district)
