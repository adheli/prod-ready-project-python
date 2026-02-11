from datetime import datetime, timedelta

from hypothesis import given, strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.services import NullCache, TaskService, UserClient


class StubUserClient(UserClient):
    def __init__(self, valid: bool = True):
        self._valid = valid

    def validate_user(self, user_id: int) -> bool:
        return self._valid


engine = create_engine("sqlite:///:memory:")
SessionTesting = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def make_service(valid_user: bool = True):
    db = SessionTesting()
    return TaskService(db, user_client=StubUserClient(valid_user), redis_client=NullCache()), db


def test_create_task_requires_valid_user():
    service, db = make_service(valid_user=False)
    try:
        service.create_task("Test", user_id=1, due_date=datetime.utcnow())
        assert False, "Expected ValueError"
    except ValueError:
        pass
    db.close()


@given(st.text(min_size=1, max_size=50))
def test_create_task_with_varied_titles(title: str):
    service, db = make_service(valid_user=True)
    task = service.create_task(title, user_id=1, due_date=datetime.utcnow() + timedelta(days=1))
    assert task.title == title
    db.close()
