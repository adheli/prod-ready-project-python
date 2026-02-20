"""
Database configuration and models for the Task Service.
This module handles SQLAlchemy engine creation, session management, and task entity definitions.
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()

TASK_DATABASE_URL = os.getenv("TASK_DATABASE_URL")
DISABLE_CHECK_SAME_THREAD = os.getenv("DISABLE_CHECK_SAME_THREAD")

ENGINE = None

if DISABLE_CHECK_SAME_THREAD.lower() == "true":
    extra_args = {"check_same_thread": False}
    ENGINE = create_engine(TASK_DATABASE_URL, poolclass=StaticPool, connect_args=extra_args)
else:
    ENGINE = create_engine(TASK_DATABASE_URL)

SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy declarative models.
    """
    __abstract__ = True


class Task(Base):
    """
    SQLAlchemy model representing a task entity in the database.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    due_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, nullable=False, index=True)


def get_task_db() -> Session:
    """
    Dependency to provide a database session for each request.
    Ensures all tables are created and handles session cleanup.
    Yields:
        Session: A SQLAlchemy database session.
    """
    Base.metadata.create_all(bind=ENGINE)
    db = SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()
