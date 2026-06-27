import json
import redis


class TaskQueue:
    QUEUE_KEY = "task_queue"

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
        self.redis_client.set(f"task:{task_id}:status", json.dumps(data), ex=1800)

    def push_reward_stream(self, task_id: int, episode: int, reward: float, epsilon: float):
        self.redis_client.xadd(
            f"task:{task_id}:reward_stream",
            {"episode": str(episode), "reward": str(reward), "epsilon": str(epsilon)},
            maxlen=5000,
        )
