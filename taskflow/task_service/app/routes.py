from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    title: str
    user_id: int
    due_date: datetime


class UpdateTaskRequest(BaseModel):
    status: str


@router.post("")
def create_task(payload: CreateTaskRequest, db: Session = Depends(get_db)):
    service = TaskService(db)
    try:
        task = service.create_task(payload.title, payload.user_id, payload.due_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "due_date": task.due_date.isoformat(),
        "user_id": task.user_id,
    }


@router.put("/{task_id}")
def update_task(task_id: int, payload: UpdateTaskRequest, db: Session = Depends(get_db)):
    service = TaskService(db)
    try:
        task = service.update_task_status(task_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "due_date": task.due_date.isoformat(),
        "user_id": task.user_id,
    }


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    try:
        service.delete_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"deleted": True}


@router.get("")
def list_tasks(
    status: Optional[str] = Query(default=None),
    due_before: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
):
    service = TaskService(db)
    tasks = service.list_tasks(status=status, due_before=due_before)
    return [
        {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "due_date": task.due_date.isoformat(),
            "user_id": task.user_id,
        }
        for task in tasks
    ]
