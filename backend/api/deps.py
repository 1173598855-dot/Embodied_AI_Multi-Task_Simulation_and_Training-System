from db.database import SessionLocal
from worker.redis_queue import TaskQueue
from config import REDIS_URL

_queue = TaskQueue(redis_url=REDIS_URL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_queue() -> TaskQueue:
    return _queue