from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TreatmentPlan(BaseModel):
    chemical: List[str]
    organic: List[str]
    dosage: Optional[str] = None

class DiseaseAnalysisResult(BaseModel):
    disease_name: str
    is_healthy: bool
    crop_type: Optional[str] = "Unknown"
    confidence: float
    symptoms: List[str]
    treatment: TreatmentPlan
    prevention: List[str]
    urgency_level: str = "Medium"  # Low, Medium, High, Critical

class DiseaseReportResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    analysis: DiseaseAnalysisResult
    created_at: datetime
