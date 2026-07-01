import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.errors import NotFoundError
from app.main import create_app


def test_app_error_uses_unified_error_envelope():
    router = APIRouter()

    @router.get("/raise-not-found")
    def raise_not_found():
        raise NotFoundError("Task not found", {"task_id": 99})

    test_app = create_app(extra_routers=[router])
    response = TestClient(test_app).get("/raise-not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "Task not found",
            "details": {"task_id": 99},
        }
    }
