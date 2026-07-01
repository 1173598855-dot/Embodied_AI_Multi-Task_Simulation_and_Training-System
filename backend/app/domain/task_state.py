from enum import StrEnum


class TaskStatus(StrEnum):
    created = "created"
    queued = "queued"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class ControlCommand(StrEnum):
    pause = "pause"
    cancel = "cancel"
