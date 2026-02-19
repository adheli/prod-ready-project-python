import logging
import os, sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
from hypothesis import given, strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

FULL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/test.env"
load_dotenv(dotenv_path=FULL_PATH, override=True)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.info(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)

from app.task_db import Base
from app.task_services import UserClient, TaskService, NullCache


class StubUserClient(UserClient):
    def __init__(self, valid: bool = True):
        super().__init__()
        self._valid = valid

    def validate_user(self, user_id: int) -> bool:
        return self._valid


def make_db():
    engine = create_engine(os.getenv("TASK_DATABASE_URL"))
    session_testing = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_testing()
    return db


def test_create_task_requires_valid_user():
    db = make_db()
    service = TaskService(db, user_client=StubUserClient(False), redis_client=NullCache())
    try:
        service.create_task("Test", user_id=1, due_date=datetime.now())
        assert False, "Expected ValueError"
    except ValueError:
        pass
    db.close()


@given(st.text(min_size=1, max_size=50))
def test_create_task_with_varied_titles(title: str):
    db = make_db()
    service = TaskService(db, user_client=StubUserClient(True), redis_client=NullCache())
    task = service.create_task(title=title, user_id=1, due_date=datetime.now() + timedelta(days=1))
    assert task.title == title
    db.close()
