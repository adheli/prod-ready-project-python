import os

from fastapi.testclient import TestClient
from user_main import app

os.environ["DATABASE_URL"] = "sqlite:///:memory"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"


client = TestClient(app)


def test_register_and_login_flow():
    register = client.post(
        "/users/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret"},
    )
    assert register.status_code == 200

    login = client.post(
        "/users/login",
        json={"email": "bob@example.com", "password": "secret"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()
