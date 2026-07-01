from fastapi import APIRouter

from app.core.config import settings
from app.infrastructure.db.database import engine
from app.infrastructure.redis.queue import TaskQueue

router = APIRouter(prefix="/health")


@router.get("/live")
def live():
    return {"status": "ok"}


@router.get("/ready")
def ready():
    checks = {"database": False, "redis": False}
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        checks["database"] = True
    except Exception:
        checks["database"] = False
    try:
        TaskQueue(redis_url=settings.REDIS_URL).redis_client.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
    status = "ok" if all(checks.values()) else "degraded"
    return {"status": status, "checks": checks}
