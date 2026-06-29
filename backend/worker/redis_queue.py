import json
import redis

from core.task_state import is_valid_control_command


class TaskQueue:
    QUEUE_KEY = "task_queue"
    EVENT_STREAM_SUFFIX = ":events"
    STATUS_KEY_SUFFIX = ":status"
    CONTROL_KEY_SUFFIX = ":control"

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.Redis.from_url(redis_url)

    def push(self, task_id: int):
        self.redis_client.lpush(self.QUEUE_KEY, task_id)

    def pop(self) -> int | None:
        raw = self.redis_client.rpop(self.QUEUE_KEY)
        return int(raw) if raw else None

    def size(self) -> int:
        return self.redis_client.llen(self.QUEUE_KEY)

    def update_status(self, task_id: int, data: dict):
        payload = json.dumps(data)
        self.redis_client.set(self._status_key(task_id), payload, ex=1800)
        self.push_event(task_id, {"type": "status_change", **data})

    def push_reward_stream(self, task_id: int, episode: int, reward: float, epsilon: float):
        self.push_event(
            task_id,
            {
                "type": "reward_update",
                "episode": episode,
                "reward": reward,
                "epsilon": epsilon,
            },
        )

    def push_event(self, task_id: int, data: dict):
        payload = {key: str(value) for key, value in data.items()}
        self.redis_client.xadd(self._event_stream_key(task_id), payload, maxlen=5000)

    def set_control_command(self, task_id: int, command: str):
        if not is_valid_control_command(command):
            raise ValueError(f"Unsupported control command: {command!r}")
        self.redis_client.set(self._control_key(task_id), command, ex=3600)

    def get_control_command(self, task_id: int) -> str | None:
        raw = self.redis_client.get(self._control_key(task_id))
        if raw is None:
            return None
        return raw.decode() if isinstance(raw, bytes) else str(raw)

    def clear_control_command(self, task_id: int):
        self.redis_client.delete(self._control_key(task_id))

    def _event_stream_key(self, task_id: int) -> str:
        return f"task:{task_id}{self.EVENT_STREAM_SUFFIX}"

    def _status_key(self, task_id: int) -> str:
        return f"task:{task_id}{self.STATUS_KEY_SUFFIX}"

    def _control_key(self, task_id: int) -> str:
        return f"task:{task_id}{self.CONTROL_KEY_SUFFIX}"
