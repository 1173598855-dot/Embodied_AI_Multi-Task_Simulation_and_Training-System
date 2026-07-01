from fastapi import APIRouter, Depends, Response

from app.api.deps import get_task_service
from app.api.schemas import TaskCreateRequest, TaskResponse
from app.application.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(task_service: TaskService = Depends(get_task_service)):
    return task_service.list_tasks()


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreateRequest, task_service: TaskService = Depends(get_task_service)):
    return task_service.create_task(body.name, body.env_type, body.env_name, body.algo, body.config)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    return task_service.get_task(task_id)


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, task_service: TaskService = Depends(get_task_service)):
    task_service.delete_task(task_id)
    return Response(status_code=204)
