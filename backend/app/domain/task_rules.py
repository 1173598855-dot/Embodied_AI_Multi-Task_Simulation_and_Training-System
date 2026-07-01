from app.domain.task_state import TaskStatus

STARTABLE = {TaskStatus.created, TaskStatus.paused, TaskStatus.failed}
PAUSABLE = {TaskStatus.queued, TaskStatus.running}
CANCELABLE = {
    TaskStatus.created,
    TaskStatus.queued,
    TaskStatus.running,
    TaskStatus.paused,
    TaskStatus.failed,
}
DELETABLE = {TaskStatus.created, TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}
TERMINAL = {TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}


def can_start(status: TaskStatus) -> bool:
    return status in STARTABLE


def can_pause(status: TaskStatus) -> bool:
    return status in PAUSABLE


def can_cancel(status: TaskStatus) -> bool:
    return status in CANCELABLE


def can_delete(status: TaskStatus) -> bool:
    return status in DELETABLE


def is_terminal(status: TaskStatus) -> bool:
    return status in TERMINAL
