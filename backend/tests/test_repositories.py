import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.db.database import Base
from app.infrastructure.db.models import TaskModel, TrainingLogModel
from app.infrastructure.db.repositories import TaskRepository, TrainingLogRepository


def make_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_task_repository_creates_and_lists_tasks_newest_first():
    session = make_session()
    repo = TaskRepository(session)
    first = repo.create(name="first", env_type="gym", env_name="CartPole-v1", algo="q_learning", config={"episodes": 1})
    second = repo.create(name="second", env_type="gym", env_name="CartPole-v1", algo="q_learning", config=None)

    tasks = repo.list()

    assert [task.id for task in tasks] == [second.id, first.id]
    assert first.status == "created"
    assert first.current_run_id is None
    assert first.error_message is None


def test_task_repository_updates_status_run_reward_and_error():
    session = make_session()
    repo = TaskRepository(session)
    task = repo.create(name="task", env_type="gym", env_name="CartPole-v1", algo="q_learning", config=None)

    repo.set_status(task.id, "running")
    repo.set_run(task.id, "run-1")
    repo.set_total_reward(task.id, 42.5)
    repo.set_error(task.id, "boom")

    updated = repo.get(task.id)
    assert updated.status == "running"
    assert updated.current_run_id == "run-1"
    assert updated.total_reward == 42.5
    assert updated.error_message == "boom"


def test_training_log_repository_creates_and_lists_by_episode():
    session = make_session()
    task_repo = TaskRepository(session)
    log_repo = TrainingLogRepository(session)
    task = task_repo.create(name="task", env_type="gym", env_name="CartPole-v1", algo="q_learning", config=None)

    log_repo.create(task_id=task.id, run_id="run-1", episode=2, step=3, reward=7.0, avg_reward=5.5)
    log_repo.create(task_id=task.id, run_id="run-1", episode=1, step=2, reward=4.0, avg_reward=4.0)

    logs = log_repo.list_by_task(task.id)

    assert [log.episode for log in logs] == [1, 2]
    assert logs[0].run_id == "run-1"


def test_deleting_task_cascades_logs():
    session = make_session()
    task_repo = TaskRepository(session)
    log_repo = TrainingLogRepository(session)
    task = task_repo.create(name="task", env_type="gym", env_name="CartPole-v1", algo="q_learning", config=None)
    log_repo.create(task_id=task.id, run_id="run-1", episode=0, step=1, reward=1.0, avg_reward=1.0)

    task_repo.delete(task.id)

    assert task_repo.get(task.id) is None
    assert log_repo.list_by_task(task.id) == []
