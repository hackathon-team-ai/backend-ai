from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CropRecommendationInput(BaseModel):
    state: str
    district: str
    season: str  # Kharif, Rabi, Zaid, Year-round
    soil_type: str  # Black, Alluvial, Red, Sandy, Clay, Loamy
    water_availability: str  # High, Medium, Rainfed / Low
    farm_size_acres: float
    budget: float

class RecommendedCrop(BaseModel):
    rank: int
    crop_name: str
    category: str
    suitability_score: float  # Percentage
    duration_days: int
    est_cost_per_acre: float
    expected_yield_per_acre: str
    est_profit_per_acre: float
    key_advantages: List[str]
    water_requirement: str
    market_demand: str

class CropRecommendationResponse(BaseModel):
    input_summary: CropRecommendationInput
    top_crops: List[RecommendedCrop]
    generated_at: datetime
