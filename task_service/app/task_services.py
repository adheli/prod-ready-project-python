"""
Service layer for managing tasks.
This module contains the business logic for task operations and clients for external services.
"""
import logging
import os
from datetime import datetime
from typing import Optional

import requests
from redis import from_url, RedisError
from sqlalchemy.orm import Session

from app.task_db import Task


class NullCache:
    """
    A fallback cache implementation that does nothing.
    Used when Redis is not available.
    """
    def setex(self, key, ttl, value):
        """
        Set a key with an expiration time in the void.
        """
        _ = (key, ttl, value)

    def delete(self, key):
        """
        Delete a key from the void cache.
        """
        _ = key


class UserClient:
    """
    Client for interacting with the User Service.
    """
    def __init__(self, base_url: Optional[str] = None):
        """
        Initializes the UserClient.
        Args:
            base_url (Optional[str]): Base URL for the User Service. 
                                     Defaults to USER_SERVICE_URL environment variable.
        """
        self.base_url = base_url or os.getenv("USER_SERVICE_URL")

    def validate_user(self, user_id: int) -> bool:
        """
        Validates if a user exists by calling the User Service.
        Args:
            user_id (int): ID of the user to validate.
        Returns:
            bool: True if user exists, False otherwise.
        """
        response = requests.get(f"{self.base_url}/users/{user_id}", timeout=3)
        return response.status_code == 200


class TaskService:
    """
    Service class for task-related business logic.
    """
    def __init__(self, db: Session, user_client: Optional[UserClient] = None, redis_client=None):
        """
        Initializes the TaskService.
        Args:
            db (Session): SQLAlchemy database session.
            user_client (Optional[UserClient]): Client for user validation.
            redis_client: Redis client for caching. Defaults to connecting via REDIS_URL.
        """
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
                    self.redis_client = from_url(redis_url)
                    logging.info("Connected to redis cache")
                except [ValueError, RedisError] as e:
                    logging.error("Error while trying to connect to redis: %s", e)
                    self.redis_client = NullCache()

    def create_task(self, title: str, user_id: int, due_date: datetime) -> Task:
        """
        Creates a new task after validating the user.
        Args:
            title (str): Task title.
            user_id (int): ID of the user who owns the task.
            due_date (datetime): Task deadline.
        Returns:
            Task: The created Task object.
        Raises:
            ValueError: If the user is unknown.
        """
        if not self.user_client.validate_user(user_id):
            raise ValueError("Unknown user")
        task = Task(title=title, user_id=user_id, due_date=due_date)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self._cache_status(task.id, task.status)
        return task

    def update_task_status(self, task_id: int, status: str) -> Task:
        """
        Updates the status of an existing task.
        Args:
            task_id (int): ID of the task to update.
            status (str): New status.
        Returns:
            Task: The updated Task object.
        Raises:
            ValueError: If the task is not found.
        """
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
        """
        Deletes a task and removes it from cache.
        Args:
            task_id (int): ID of the task to delete.
        Raises:
            ValueError: If the task is not found.
        """
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
        """
        Lists tasks with optional status and due date filters.
        Args:
            status (Optional[str]): Filter by task status.
            due_before (Optional[datetime]): Filter tasks due on or before this date.
        Returns:
            List[Task]: List of Task objects.
        """
        query = self.db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        if due_before:
            query = query.filter(Task.due_date <= due_before)
        return query.all()

    def _cache_status(self, task_id: int, status: str) -> None:
        """
        Caches the task status in Redis.
        Args:
            task_id (int): Task ID.
            status (str): Status to cache.
        """
        try:
            self.redis_client.setex(f"task:{task_id}", 300, status)
        except RuntimeError:
            logging.error("Failed to cache task status in redis")
