import os

from dotenv import load_dotenv
from fastapi.testclient import TestClient

FULL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/test.env"
load_dotenv(dotenv_path=FULL_PATH, override=True)

from app.main import app

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
