import redis

from app.core.config import settings
from app.domain.task_state import ControlCommand


class TaskControl:
    def __init__(self, redis_client=None, redis_url: str | None = None):
        self.redis_client = redis_client or redis.Redis.from_url(redis_url or settings.REDIS_URL)

    def set_command(self, task_id: int, command: ControlCommand) -> None:
        self.redis_client.set(self._control_key(task_id), command.value, ex=settings.TASK_CONTROL_TTL)

    def get_command(self, task_id: int) -> ControlCommand | None:
        raw = self.redis_client.get(self._control_key(task_id))
        if raw is None:
            return None
        value = raw.decode() if isinstance(raw, bytes) else str(raw)
        return ControlCommand(value)

    def clear_command(self, task_id: int) -> None:
        self.redis_client.delete(self._control_key(task_id))

    def _control_key(self, task_id: int) -> str:
        return f"embodied_ai:task:{task_id}:control"
