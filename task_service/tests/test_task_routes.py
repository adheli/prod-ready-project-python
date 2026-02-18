import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi.testclient import TestClient

FULL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/test.env"
load_dotenv(dotenv_path=FULL_PATH, override=True)

import task_services
from task_main import api


def test_create_and_list_task_flow(monkeypatch):
    monkeypatch.setattr(task_services.UserClient, "validate_user", lambda self, user_id: True)
    client = TestClient(api)

    create = client.post(
        "/tasks",
        json={
            "title": "Build docs",
            "user_id": 1,
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
        },
    )
    assert create.status_code == 201
    assert create.json()["title"] == "Build docs"

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
