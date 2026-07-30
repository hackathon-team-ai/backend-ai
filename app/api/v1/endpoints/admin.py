from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.admin import SystemAnalytics

router = APIRouter()

@router.get("/analytics", response_model=SystemAnalytics)
async def get_admin_analytics(current_user: dict = Depends(get_current_user)):
    # Verify user role or allow for demo
    return SystemAnalytics(
        total_users=142,
        active_users=98,
        total_chats=1240,
        disease_scans=312,
        documents_indexed=85,
        active_tasks=240,
        recent_activity=[
            {"user": "Ramesh Kumar", "action": "Scanned Tomato leaf image", "status": "Found Early Blight", "time": "10 mins ago"},
            {"user": "Suresh Patel", "action": "Queried RAG vector DB on Wheat MSP", "status": "Success", "time": "25 mins ago"},
            {"user": "Anita Devi", "action": "Ran Crop Advisor calculator", "status": "Matched Chickpea & Soybean", "time": "1 hour ago"}
        ],
        chat_category_breakdown={
            "Fertilizers": 340,
            "Diseases": 280,
            "Crop Selection": 220,
            "Weather": 190,
            "Irrigation": 120,
            "Organic Farming": 90
        },
        disease_detection_trends=[
            {"month": "Jan", "Early Blight": 45, "Yellow Rust": 20, "Rice Blast": 15},
            {"month": "Feb", "Early Blight": 55, "Yellow Rust": 35, "Rice Blast": 25},
            {"month": "Mar", "Early Blight": 70, "Yellow Rust": 50, "Rice Blast": 40},
            {"month": "Apr", "Early Blight": 62, "Yellow Rust": 38, "Rice Blast": 55}
        ]
    )

@router.get("/users")
async def list_users(current_user: dict = Depends(get_current_user)):
    return [
        {"id": "u1", "full_name": "Ramesh Kumar", "email": "ramesh@example.com", "role": "farmer", "state": "Punjab", "district": "Ludhiana", "status": "Active"},
        {"id": "u2", "full_name": "Dr. Sunita Sharma", "email": "sunita@agri.gov.in", "role": "agronomist", "state": "Maharashtra", "district": "Pune", "status": "Active"},
        {"id": "u3", "full_name": "Rajesh Patel", "email": "rajesh@example.com", "role": "farmer", "state": "Gujarat", "district": "Rajkot", "status": "Active"},
        {"id": "u4", "full_name": "Admin User", "email": "admin@krishimitra.ai", "role": "admin", "state": "Delhi", "district": "New Delhi", "status": "Active"}
    ]
