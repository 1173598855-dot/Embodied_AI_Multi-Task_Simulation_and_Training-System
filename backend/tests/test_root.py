import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def test_root_route_returns_service_info():
    response = TestClient(app).get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Embodied AI Training Platform"
    assert body["status"] == "ok"
    assert body["docs"] == "/docs"
