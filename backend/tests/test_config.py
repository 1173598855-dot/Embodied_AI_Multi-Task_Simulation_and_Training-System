import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings


def test_settings_defaults_are_enterprise_safe():
    assert settings.DATABASE_URL.startswith("mysql+pymysql://")
    assert settings.REDIS_URL.startswith("redis://")
    assert settings.TASK_QUEUE_KEY == "embodied_ai:task_queue"
    assert settings.EVENT_STREAM_MAXLEN == 5000
    assert settings.TASK_CONTROL_TTL == 3600
    assert settings.ENV in {"development", "test", "production"}
