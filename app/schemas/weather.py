from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DailyForecast(BaseModel):
    date: str
    day_name: str
    temp_max: float
    temp_min: float
    humidity: int
    rain_probability: int
    condition: str
    icon: str

class WeatherResponse(BaseModel):
    location: str
    state: str
    current_temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    rain_probability: int
    condition: str
    uv_index: float
    agri_recommendations: List[str]
    forecast: List[DailyForecast]
    updated_at: datetime
