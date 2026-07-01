import redis

from app.core.config import settings


class EventStream:
    def __init__(self, redis_client=None, redis_url: str | None = None):
        self.redis_client = redis_client or redis.Redis.from_url(redis_url or settings.REDIS_URL)

    def publish(self, task_id: int, event: dict) -> None:
        payload = {key: str(value) for key, value in event.items() if value is not None}
        self.redis_client.xadd(self._stream_key(task_id), payload, maxlen=settings.EVENT_STREAM_MAXLEN)

    def read(self, task_id: int, last_id: str, count: int = 10, block_ms: int = 2000) -> list[tuple[str, dict]]:
        entries = self.redis_client.xread({self._stream_key(task_id): last_id}, count=count, block=block_ms)
        decoded: list[tuple[str, dict]] = []
        for _stream_name, messages in entries:
            for message_id, fields in messages:
                decoded_id = message_id.decode() if isinstance(message_id, bytes) else str(message_id)
                decoded_fields = {
                    key.decode() if isinstance(key, bytes) else str(key): value.decode() if isinstance(value, bytes) else str(value)
                    for key, value in fields.items()
                }
                decoded.append((decoded_id, decoded_fields))
        return decoded

    def _stream_key(self, task_id: int) -> str:
        return f"embodied_ai:task:{task_id}:events"
