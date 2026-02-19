import logging
import os
from datetime import datetime
from typing import Optional

import redis
import requests
from sqlalchemy.orm import Session

from task_db import Task


class NullCache:
    def setex(self, key, ttl, value):
        _ = (key, ttl, value)

    def delete(self, key):
        _ = key


class UserClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("USER_SERVICE_URL")

    def validate_user(self, user_id: int) -> bool:
        response = requests.get(f"{self.base_url}/users/{user_id}", timeout=3)
        return response.status_code == 200


class TaskService:
    def __init__(self, db: Session, user_client: Optional[UserClient] = None, redis_client=None):
        self.db = db
        self.user_client = user_client or UserClient()
        if redis_client is not None:
            self.redis_client = redis_client
        else:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                logging.warning("No redis URL found, using NullCache")
                self.redis_client = NullCache()
            else:
                try:
                    self.redis_client = redis.from_url(redis_url)
                    logging.info("Connected to redis cache")
                except Exception as e:
                    logging.error(f"Error while trying to connect to redis: {e}")
                    self.redis_client = NullCache()

    def create_task(self, title: str, user_id: int, due_date: datetime) -> Task:
        if not self.user_client.validate_user(user_id):
            raise ValueError("Unknown user")
        task = Task(title=title, user_id=user_id, due_date=due_date)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self._cache_status(task.id, task.status)
        return task

    def update_task_status(self, task_id: int, status: str) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        task.status = status
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self._cache_status(task.id, task.status)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found")
        self.db.delete(task)
        self.db.commit()
        try:
            self.redis_client.delete(f"task:{task_id}")
        except RuntimeError:
            logging.error("Failed to delete task from redis cache")

    def list_tasks(self, status: Optional[str] = None, due_before: Optional[datetime] = None):
        query = self.db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        if due_before:
            query = query.filter(Task.due_date <= due_before)
        return query.all()

    def _cache_status(self, task_id: int, status: str) -> None:
        try:
            self.redis_client.setex(f"task:{task_id}", 300, status)
        except RuntimeError:
            logging.error("Failed to cache task status in redis")
