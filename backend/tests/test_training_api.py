import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.api.deps import get_task_service, get_training_log_service
from app.main import app


class Task:
    id = 1
    name = "demo"
    env_type = "gym"
    env_name = "CartPole-v1"
    algo = "q_learning"
    status = "queued"
    config = None
    total_reward = None
    current_run_id = "run-1"
    error_message = None
    created_at = None
    updated_at = None


class Log:
    id = 1
    task_id = 1
    run_id = "run-1"
    episode = 0
    step = 1
    reward = 1.0
    avg_reward = 1.0
    created_at = None


class FakeTaskService:
    def start_task(self, task_id):
        return Task()

    def pause_task(self, task_id):
        task = Task()
        task.status = "paused"
        return task

    def cancel_task(self, task_id):
        task = Task()
        task.status = "canceled"
        return task


class FakeLogService:
    def list_logs(self, task_id):
        return [Log()]


def test_training_routes_call_services():
    app.dependency_overrides[get_task_service] = lambda: FakeTaskService()
    app.dependency_overrides[get_training_log_service] = lambda: FakeLogService()
    client = TestClient(app)
    try:
        assert client.post("/api/training/1/start").json()["status"] == "queued"
        assert client.post("/api/training/1/pause").json()["status"] == "paused"
        assert client.post("/api/training/1/cancel").json()["status"] == "canceled"
        logs = client.get("/api/training/1/logs").json()
        assert logs[0]["run_id"] == "run-1"
    finally:
        app.dependency_overrides.clear()
