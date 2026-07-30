import uuid
from datetime import datetime, date
from typing import List
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.calendar import TaskCreate, TaskResponse

router = APIRouter()
IN_MEMORY_TASKS = [
    TaskResponse(
        id="task_01",
        user_id="demo_user",
        crop_name="Wheat (HD-2967)",
        stage="Irrigation",
        title="First Crown Root Irrigation",
        description="Apply 2-inch light irrigation 21 days after sowing during CRI stage.",
        due_date=date.today().strftime("%Y-%m-%d"),
        priority="High",
        completed=False,
        created_at=datetime.utcnow()
    ),
    TaskResponse(
        id="task_02",
        user_id="demo_user",
        crop_name="Wheat (HD-2967)",
        stage="Fertilizer",
        title="Top Dressing Urea (1st Split)",
        description="Apply 30 kg Urea per acre post CRI irrigation when soil is damp.",
        due_date=(date.today()).strftime("%Y-%m-%d"),
        priority="Medium",
        completed=True,
        created_at=datetime.utcnow()
    )
]

@router.get("", response_model=List[TaskResponse])
async def list_tasks(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    tasks = [t for t in IN_MEMORY_TASKS if t.user_id == user_id or t.user_id == "demo_user"]
    return tasks

@router.post("", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    t = TaskResponse(
        id=f"task_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        crop_name=task_in.crop_name,
        stage=task_in.stage,
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        completed=False,
        created_at=datetime.utcnow()
    )
    IN_MEMORY_TASKS.append(t)
    return t

@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    for t in IN_MEMORY_TASKS:
        if t.id == task_id:
            t.completed = not t.completed
            return t
    raise HTTPException(status_code=404, detail="Task not found.")
