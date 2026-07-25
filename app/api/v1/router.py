from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    chat,
    rag,
    disease,
    weather,
    crop,
    schemes,
    calendar,
    dashboard,
    admin
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Agriculture Chatbot"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG Knowledge Base"])
api_router.include_router(disease.router, prefix="/disease", tags=["Image Disease Detection"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Intelligence"])
api_router.include_router(crop.router, prefix="/crop", tags=["Crop Recommendation Engine"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["Government Schemes"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Smart Farming Calendar"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Summary"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Control Panel"])
