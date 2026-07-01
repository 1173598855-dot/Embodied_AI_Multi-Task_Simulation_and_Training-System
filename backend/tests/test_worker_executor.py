import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.infrastructure.redis.queue import QueuedTaskMessage
from app.worker.executor import WorkerExecutor


class Task:
    def __init__(self):
        self.id = 1
        self.env_type = "gym"
        self.env_name = "CartPole-v1"
        self.config = {"episodes": 2}
        self.status = "queued"
        self.current_run_id = None


class FakeTaskRepository:
    def __init__(self):
        self.task = Task()
        self.statuses = []
        self.errors = []
        self.rewards = []
        self.runs = []

    def get(self, task_id):
        return self.task if task_id == self.task.id else None

    def set_status(self, task_id, status):
        self.task.status = status
        self.statuses.append(status)
        return self.task

    def set_run(self, task_id, run_id):
        self.task.current_run_id = run_id
        self.runs.append(run_id)
        return self.task

    def set_total_reward(self, task_id, reward):
        self.rewards.append(reward)
        return self.task

    def set_error(self, task_id, error_message):
        self.errors.append(error_message)
        return self.task


class FakeLogRepository:
    def __init__(self):
        self.logs = []

    def create(self, task_id, run_id, episode, step, reward, avg_reward):
        self.logs.append((task_id, run_id, episode, step, reward, avg_reward))


class FakeEventStream:
    def __init__(self):
        self.events = []

    def publish(self, task_id, event):
        self.events.append((task_id, event))


class FakeControl:
    def __init__(self, command=None):
        self.command = command

    def get_command(self, task_id):
        return self.command

    def clear_command(self, task_id):
        self.command = None


class FakeTrainer:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def run(self, episodes, on_episode, on_control):
        if self.error:
            raise self.error
        on_episode(1, "run-1", 0, 5.0, 0.5)
        if self.result:
            return self.result
        on_episode(1, "run-1", 1, 7.0, 0.4)
        return None


def make_executor(trainer):
    task_repo = FakeTaskRepository()
    log_repo = FakeLogRepository()
    event_stream = FakeEventStream()
    control = FakeControl()
    executor = WorkerExecutor(
        task_repository=task_repo,
        training_log_repository=log_repo,
        event_stream=event_stream,
        task_control=control,
        trainer_factory=lambda task, run_id: trainer,
    )
    return executor, task_repo, log_repo, event_stream


def test_worker_completes_task_and_records_logs_events_and_reward():
    executor, task_repo, log_repo, event_stream = make_executor(FakeTrainer())

    executor.execute(QueuedTaskMessage(task_id=1, run_id="run-1", attempt=1))

    assert task_repo.statuses == ["running", "completed"]
    assert task_repo.runs == ["run-1"]
    assert task_repo.rewards == [7.0]
    assert [log[2] for log in log_repo.logs] == [0, 1]
    assert [event[1]["type"] for event in event_stream.events] == [
        "status_changed",
        "episode_completed",
        "episode_completed",
        "status_changed",
    ]


def test_worker_marks_paused_when_trainer_returns_pause():
    executor, task_repo, _log_repo, _event_stream = make_executor(FakeTrainer(result="pause"))

    executor.execute(QueuedTaskMessage(task_id=1, run_id="run-1", attempt=1))

    assert task_repo.statuses[-1] == "paused"


def test_worker_marks_canceled_when_trainer_returns_cancel():
    executor, task_repo, _log_repo, _event_stream = make_executor(FakeTrainer(result="cancel"))

    executor.execute(QueuedTaskMessage(task_id=1, run_id="run-1", attempt=1))

    assert task_repo.statuses[-1] == "canceled"


def test_worker_marks_failed_and_publishes_failure_event_on_exception():
    executor, task_repo, _log_repo, event_stream = make_executor(FakeTrainer(error=RuntimeError("boom")))

    executor.execute(QueuedTaskMessage(task_id=1, run_id="run-1", attempt=1))

    assert task_repo.statuses[-1] == "failed"
    assert task_repo.errors == ["boom"]
    assert event_stream.events[-1][1]["type"] == "task_failed"
