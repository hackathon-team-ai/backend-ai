from fastapi import APIRouter, Depends
from app.api.v1.endpoints.auth import get_current_user
from app.services.weather_service import weather_service

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    user_state = current_user.get("state", "Maharashtra")
    user_district = current_user.get("district", "Pune")
    
    weather = await weather_service.get_weather_data(state=user_state, district=user_district)
    
    return {
        "user_name": current_user.get("full_name", "Farmer"),
        "role": current_user.get("role", "farmer"),
        "farm_size": current_user.get("farm_size_acres", 2.5),
        "district": user_district,
        "state": user_state,
        "weather_widget": {
            "temp": weather.current_temp,
            "condition": weather.condition,
            "humidity": weather.humidity,
            "rain_prob": weather.rain_probability,
            "tip": weather.agri_recommendations[0] if weather.agri_recommendations else "Regular scouting recommended."
        },
        "stats": {
            "total_chats": 12,
            "disease_scans": 4,
            "documents_indexed": 3,
            "pending_calendar_tasks": 2,
            "health_score": "92% Healthy"
        },
        "recent_chats": [
            {"id": "c1", "title": "Best fertilizer dose for Wheat", "category": "Fertilizers", "time": "2 hours ago"},
            {"id": "c2", "title": "Yellow spots on Tomato leaf", "category": "Diseases", "time": "Yesterday"},
            {"id": "c3", "title": "Drip irrigation timing guide", "category": "Irrigation", "time": "3 days ago"}
        ]
    }
