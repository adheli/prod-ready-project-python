from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    due_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, nullable=False, index=True)
