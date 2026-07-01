import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.application.task_service import TaskService
from app.core.errors import ConflictError, NotFoundError
from app.domain.task_state import ControlCommand


class FakeTask:
    def __init__(self, id, status="created"):
        self.id = id
        self.name = "task"
        self.env_type = "gym"
        self.env_name = "CartPole-v1"
        self.algo = "q_learning"
        self.config = None
        self.status = status
        self.current_run_id = None


class FakeTaskRepository:
    def __init__(self):
        self.tasks = {}
        self.next_id = 1
        self.deleted = []

    def create(self, name, env_type, env_name, algo, config):
        task = FakeTask(self.next_id)
        task.name = name
        task.env_type = env_type
        task.env_name = env_name
        task.algo = algo
        task.config = config
        self.tasks[task.id] = task
        self.next_id += 1
        return task

    def get(self, task_id):
        return self.tasks.get(task_id)

    def list(self):
        return list(reversed(list(self.tasks.values())))

    def delete(self, task_id):
        self.deleted.append(task_id)
        self.tasks.pop(task_id, None)

    def set_status(self, task_id, status):
        self.tasks[task_id].status = status
        return self.tasks[task_id]

    def set_run(self, task_id, run_id):
        self.tasks[task_id].current_run_id = run_id
        return self.tasks[task_id]


class FakeQueue:
    def __init__(self):
        self.messages = []

    def enqueue(self, task_id, run_id, attempt=1):
        self.messages.append((task_id, run_id, attempt))


class FakeControl:
    def __init__(self):
        self.commands = []
        self.cleared = []

    def set_command(self, task_id, command):
        self.commands.append((task_id, command))

    def clear_command(self, task_id):
        self.cleared.append(task_id)


def make_service():
    repo = FakeTaskRepository()
    queue = FakeQueue()
    control = FakeControl()
    return TaskService(repo, queue, control), repo, queue, control


def test_create_task_defaults_to_created():
    service, repo, _queue, _control = make_service()

    task = service.create_task("demo", "gym", "CartPole-v1", "q_learning", {"episodes": 3})

    assert task.id == 1
    assert task.status == "created"
    assert repo.get(1).config == {"episodes": 3}


def test_start_task_sets_queued_run_and_enqueues_message():
    service, repo, queue, control = make_service()
    task = service.create_task("demo", "gym", "CartPole-v1", "q_learning", None)

    started = service.start_task(task.id)

    assert started.status == "queued"
    assert started.current_run_id.startswith("run-")
    assert queue.messages == [(task.id, started.current_run_id, 1)]
    assert control.cleared == [task.id]


def test_start_task_rejects_running_task():
    service, repo, _queue, _control = make_service()
    task = service.create_task("demo", "gym", "CartPole-v1", "q_learning", None)
    repo.set_status(task.id, "running")

    with pytest.raises(ConflictError):
        service.start_task(task.id)


def test_pause_and_cancel_create_control_commands():
    service, repo, _queue, control = make_service()
    task = service.create_task("demo", "gym", "CartPole-v1", "q_learning", None)
    repo.set_status(task.id, "running")

    paused = service.pause_task(task.id)
    assert paused.status == "paused"

    canceled = service.cancel_task(task.id)

    assert canceled.status == "canceled"
    assert control.commands == [(task.id, ControlCommand.pause), (task.id, ControlCommand.cancel)]


def test_delete_task_uses_domain_delete_rules():
    service, repo, _queue, _control = make_service()
    task = service.create_task("demo", "gym", "CartPole-v1", "q_learning", None)

    service.delete_task(task.id)

    assert repo.deleted == [task.id]
    assert repo.get(task.id) is None


def test_missing_task_raises_not_found():
    service, _repo, _queue, _control = make_service()

    with pytest.raises(NotFoundError):
        service.get_task(999)

