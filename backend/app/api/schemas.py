from datetime import datetime

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict = {}


class ErrorEnvelope(BaseModel):
    error: ErrorBody


class TaskCreateRequest(BaseModel):
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
    current_run_id: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TrainingLogResponse(BaseModel):
    id: int
    task_id: int
    run_id: str | None = None
    episode: int
    step: int
    reward: float
    avg_reward: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
