import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/embodied_ai")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    TASK_QUEUE_KEY: str = os.getenv("TASK_QUEUE_KEY", "embodied_ai:task_queue")
    EVENT_STREAM_MAXLEN: int = int(os.getenv("EVENT_STREAM_MAXLEN", "5000"))
    TASK_CONTROL_TTL: int = int(os.getenv("TASK_CONTROL_TTL", "3600"))
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv(
        "LOG_LEVEL",
        "DEBUG" if os.getenv("ENV", "development") == "development" else "INFO",
    )


settings = Settings()
