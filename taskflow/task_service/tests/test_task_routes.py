import os
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

import task_services
from task_main import api

os.environ["DATABASE_URL"] = "sqlite:///./test_task_routes.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["USER_SERVICE_URL"] = "http://example.com"


client = TestClient(api)


def test_create_and_list_task_flow(monkeypatch):
    monkeypatch.setattr(task_services.UserClient, "validate_user", lambda self, user_id: True)

    create = client.post(
        "/tasks",
        json={
            "title": "Build docs",
            "user_id": 1,
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        },
    )
    assert create.status_code == 200

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
