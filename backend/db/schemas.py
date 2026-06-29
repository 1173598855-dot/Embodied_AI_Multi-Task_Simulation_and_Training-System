from datetime import datetime

from pydantic import BaseModel

from core.task_state import VALID_STATUSES


class TaskCreate(BaseModel):
    name: str
    env_type: str = "gym"
    env_name: str = "CartPole-v1"
    algo: str = "q_learning"
    config: dict | None = None


class TaskResponse(BaseModel):
    id: int
    name: str
    env_type: str
    env_name: str
    algo: str
    status: str
    config: dict | None = None
    total_reward: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}

    @classmethod
    def valid_statuses(cls) -> set[str]:
        return set(VALID_STATUSES)


class TrainingLogResponse(BaseModel):
    id: int
    task_id: int
    episode: int
    step: int
    reward: float
    avg_reward: float | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}
