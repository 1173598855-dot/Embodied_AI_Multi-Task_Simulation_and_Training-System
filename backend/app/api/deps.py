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


def get_task_repository(session=next(get_db_session())):
    return TaskRepository(session)


def get_training_log_repository(session=next(get_db_session())):
    return TrainingLogRepository(session)
