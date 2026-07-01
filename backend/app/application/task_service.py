from uuid import uuid4

from app.core.errors import ConflictError, NotFoundError
from app.domain.task_rules import can_cancel, can_delete, can_pause, can_start
from app.domain.task_state import ControlCommand, TaskStatus


class TaskService:
    def __init__(self, task_repository, task_queue, task_control):
        self.task_repository = task_repository
        self.task_queue = task_queue
        self.task_control = task_control

    def create_task(self, name: str, env_type: str, env_name: str, algo: str, config: dict | None):
        return self.task_repository.create(name, env_type, env_name, algo, config)

    def get_task(self, task_id: int):
        task = self.task_repository.get(task_id)
        if task is None:
            raise NotFoundError("Task not found", {"task_id": task_id})
        return task

    def list_tasks(self):
        return self.task_repository.list()

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        status = TaskStatus(task.status)
        if not can_delete(status):
            raise ConflictError(f"Task cannot be deleted from status {task.status}", {"task_id": task_id})
        self.task_repository.delete(task_id)

    def start_task(self, task_id: int):
        task = self.get_task(task_id)
        status = TaskStatus(task.status)
        if not can_start(status):
            raise ConflictError(f"Task cannot be started from status {task.status}", {"task_id": task_id})
        run_id = f"run-{uuid4().hex}"
        self.task_control.clear_command(task_id)
        self.task_repository.set_run(task_id, run_id)
        queued = self.task_repository.set_status(task_id, TaskStatus.queued.value)
        self.task_queue.enqueue(task_id, run_id, attempt=1)
        return queued

    def pause_task(self, task_id: int):
        task = self.get_task(task_id)
        status = TaskStatus(task.status)
        if not can_pause(status):
            raise ConflictError(f"Task cannot be paused from status {task.status}", {"task_id": task_id})
        self.task_control.set_command(task_id, ControlCommand.pause)
        return self.task_repository.set_status(task_id, TaskStatus.paused.value)

    def cancel_task(self, task_id: int):
        task = self.get_task(task_id)
        status = TaskStatus(task.status)
        if not can_cancel(status):
            raise ConflictError(f"Task cannot be canceled from status {task.status}", {"task_id": task_id})
        self.task_control.set_command(task_id, ControlCommand.cancel)
        return self.task_repository.set_status(task_id, TaskStatus.canceled.value)
