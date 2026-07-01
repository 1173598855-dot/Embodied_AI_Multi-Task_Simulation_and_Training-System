import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.api.deps import get_task_service
from app.main import app


class Task:
    def __init__(self, id=1, status="created"):
        self.id = id
        self.name = "demo"
        self.env_type = "gym"
        self.env_name = "CartPole-v1"
        self.algo = "q_learning"
        self.status = status
        self.config = None
        self.total_reward = None
        self.current_run_id = None
        self.error_message = None
        self.created_at = None
        self.updated_at = None


class FakeTaskService:
    def __init__(self):
        self.task = Task()
        self.deleted = []

    def list_tasks(self):
        return [self.task]

    def create_task(self, name, env_type, env_name, algo, config):
        self.task.name = name
        self.task.env_type = env_type
        self.task.env_name = env_name
        self.task.algo = algo
        self.task.config = config
        return self.task

    def get_task(self, task_id):
        return self.task

    def delete_task(self, task_id):
        self.deleted.append(task_id)


def test_task_routes_call_task_service():
    service = FakeTaskService()
    app.dependency_overrides[get_task_service] = lambda: service
    client = TestClient(app)
    try:
        assert client.get("/api/tasks").json()[0]["name"] == "demo"
        created = client.post("/api/tasks", json={"name": "new", "config": {"episodes": 1}}).json()
        assert created["name"] == "new"
        assert created["config"] == {"episodes": 1}
        assert client.get("/api/tasks/1").json()["id"] == 1
        assert client.delete("/api/tasks/1").status_code == 204
        assert service.deleted == [1]
    finally:
        app.dependency_overrides.clear()
