import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings
from app.schemas.disease import DiseaseReportResponse
from app.services.disease_service import disease_service

router = APIRouter()
IN_MEMORY_DISEASE_REPORTS = []

@router.post("/analyze", response_model=DiseaseReportResponse)
async def upload_and_analyze_leaf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid image file format. Upload JPG or PNG.")

    filename = f"leaf_{uuid.uuid4().hex[:10]}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    analysis = await disease_service.analyze_leaf_image(filepath, file.filename)
    report_id = f"report_{uuid.uuid4().hex[:8]}"
    image_url = f"/static/{filename}"

    report = DiseaseReportResponse(
        id=report_id,
        user_id=user_id,
        image_url=image_url,
        analysis=analysis,
        created_at=datetime.utcnow()
    )

    IN_MEMORY_DISEASE_REPORTS.append(report)
    return report

@router.get("/reports", response_model=List[DiseaseReportResponse])
async def list_disease_reports(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    reports = [r for r in IN_MEMORY_DISEASE_REPORTS if r.user_id == user_id]
    reports.sort(key=lambda x: x.created_at, reverse=True)
    return reports
