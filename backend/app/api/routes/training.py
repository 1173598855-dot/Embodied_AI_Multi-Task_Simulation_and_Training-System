from fastapi import APIRouter, Depends

from app.api.deps import get_task_service, get_training_log_service
from app.api.schemas import TaskResponse, TrainingLogResponse
from app.application.task_service import TaskService
from app.application.training_log_service import TrainingLogService

router = APIRouter(prefix="/api/training", tags=["training"])


@router.post("/{task_id}/start", response_model=TaskResponse)
def start_training(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return task_service.start_task(task_id)


@router.post("/{task_id}/pause", response_model=TaskResponse)
def pause_training(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return task_service.pause_task(task_id)


@router.post("/{task_id}/cancel", response_model=TaskResponse)
def cancel_training(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return task_service.cancel_task(task_id)


@router.get("/{task_id}/logs", response_model=list[TrainingLogResponse])
def get_training_logs(
    task_id: int,
    training_log_service: TrainingLogService = Depends(get_training_log_service),
):
    return training_log_service.list_logs(task_id)
