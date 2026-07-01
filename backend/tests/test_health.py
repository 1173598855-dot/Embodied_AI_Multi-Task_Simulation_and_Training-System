import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app


def test_live_health_route_returns_ok():
    response = TestClient(app).get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_health_route_uses_dependency_checks():
    response = TestClient(app).get("/health/ready")

    assert response.status_code in {200, 503}
    body = response.json()
    assert "status" in body
    assert "checks" in body
