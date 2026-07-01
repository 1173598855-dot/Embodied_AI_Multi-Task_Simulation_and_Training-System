import json
from dataclasses import dataclass

import redis

from app.core.config import settings


@dataclass(frozen=True)
class QueuedTaskMessage:
    task_id: int
    run_id: str
    attempt: int = 1


class TaskQueue:
    def __init__(self, redis_client=None, redis_url: str | None = None, queue_key: str | None = None):
        self.redis_client = redis_client or redis.Redis.from_url(redis_url or settings.REDIS_URL)
        self.queue_key = queue_key or settings.TASK_QUEUE_KEY

    def enqueue(self, task_id: int, run_id: str, attempt: int = 1) -> None:
        payload = json.dumps({"task_id": task_id, "run_id": run_id, "attempt": attempt})
        self.redis_client.lpush(self.queue_key, payload)

    def dequeue(self) -> QueuedTaskMessage | None:
        raw = self.redis_client.rpop(self.queue_key)
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        try:
            payload = json.loads(raw)
            return QueuedTaskMessage(
                task_id=int(payload["task_id"]),
                run_id=str(payload["run_id"]),
                attempt=int(payload.get("attempt", 1)),
            )
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            return None

    def size(self) -> int:
        return int(self.redis_client.llen(self.queue_key))
