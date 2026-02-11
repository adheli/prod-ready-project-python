from hypothesis import given, strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.services import JWTManager, UserService


engine = create_engine("sqlite:///:memory:")
SessionTesting = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def make_service():
    db = SessionTesting()
    return UserService(db), db


def test_create_and_authenticate_user():
    service, db = make_service()
    user = service.create_user("Alice", "alice@example.com", "secret")
    assert user.id is not None
    assert service.authenticate("alice@example.com", "secret") is not None
    db.close()


@given(st.integers(min_value=1, max_value=10_000))
def test_jwt_manager_contains_user_id(user_id: int):
    token = JWTManager(secret="test-secret").create_token(user_id)
    body_hex, _ = token.split(".")
    body = bytes.fromhex(body_hex).decode("utf-8")
    assert f'"user_id":{user_id}' in body
