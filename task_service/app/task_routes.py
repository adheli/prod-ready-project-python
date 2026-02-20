"""
FastAPI route definitions for task-related operations.
This module defines the endpoints for creating, updating, deleting, and listing tasks.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.task_db import get_task_db
from app.task_services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """
    Pydantic model for task creation request payload.
    """
    title: str
    user_id: int
    due_date: datetime


class UpdateTaskRequest(BaseModel):
    """
    Pydantic model for task update request payload.
    """
    status: str


@router.post("", status_code=201)
def create_task(payload: CreateTaskRequest, db: Session = Depends(get_task_db)):
    """
    Endpoint to create a new task.
    Args:
        payload (CreateTaskRequest): Task details (title, user_id, due_date).
        db (Session): Database session provided by dependency injection.
    Returns:
        dict: The created task details.
    Raises:
        HTTPException: If user validation fails.
    """
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
def update_task(task_id: int, payload: UpdateTaskRequest, db: Session = Depends(get_task_db)):
    """
    Endpoint to update the status of an existing task.
    Args:
        task_id (int): ID of the task to update.
        payload (UpdateTaskRequest): New status for the task.
        db (Session): Database session.
    Returns:
        dict: Updated task details.
    Raises:
        HTTPException: If the task is not found.
    """
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
def delete_task(task_id: int, db: Session = Depends(get_task_db)):
    """
    Endpoint to delete a task.
    Args:
        task_id (int): ID of the task to delete.
        db (Session): Database session.
    Returns:
        dict: Deletion confirmation.
    Raises:
        HTTPException: If the task is not found.
    """
    service = TaskService(db)
    try:
        service.delete_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"deleted": True}


@router.get("")
def list_tasks(status: Optional[str] = Query(default=None),
               due_before: Optional[datetime] = Query(default=None),
               db: Session = Depends(get_task_db)
               ):
    """
    Endpoint to list tasks with optional filtering.
    Args:
        status (Optional[str]): Filter by task status.
        due_before (Optional[datetime]): Filter tasks due before this timestamp.
        db (Session): Database session.
    Returns:
        list[dict]: List of task details matching the filters.
    """
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
