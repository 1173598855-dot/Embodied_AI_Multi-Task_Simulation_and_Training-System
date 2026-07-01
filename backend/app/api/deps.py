from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.task_service import TaskService
from app.application.training_log_service import TrainingLogService
from app.infrastructure.db.database import session_scope
from app.infrastructure.db.repositories import TaskRepository, TrainingLogRepository
from app.infrastructure.redis.control import TaskControl
from app.infrastructure.redis.events import EventStream
from app.infrastructure.redis.queue import TaskQueue


def get_db_session():
    with session_scope() as session:
        yield session


def get_task_queue() -> TaskQueue:
    return TaskQueue()


def get_task_control() -> TaskControl:
    return TaskControl()


def get_event_stream() -> EventStream:
    return EventStream()


def get_task_repository(session: Session = Depends(get_db_session)) -> TaskRepository:
    return TaskRepository(session)


def get_training_log_repository(session: Session = Depends(get_db_session)) -> TrainingLogRepository:
    return TrainingLogRepository(session)


def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
    task_queue: TaskQueue = Depends(get_task_queue),
    task_control: TaskControl = Depends(get_task_control),
) -> TaskService:
    return TaskService(task_repository, task_queue, task_control)


def get_training_log_service(
    training_log_repository: TrainingLogRepository = Depends(get_training_log_repository),
) -> TrainingLogService:
    return TrainingLogService(training_log_repository)
