import os
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
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
    if not file.filename:
        raise HTTPException(status_code=400, detail="Please select an image file.")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Upload a JPG, PNG, or WEBP file.")

    content = await file.read()
    if not content or len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be between 1 byte and 10 MB.")
    try:
        from io import BytesIO
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.")

    filename = f"leaf_{uuid.uuid4().hex[:10]}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
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
