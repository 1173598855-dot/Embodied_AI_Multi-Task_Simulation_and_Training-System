import time

from app.infrastructure.db.database import session_scope
from app.infrastructure.db.repositories import TaskRepository, TrainingLogRepository
from app.infrastructure.redis.control import TaskControl
from app.infrastructure.redis.events import EventStream
from app.infrastructure.redis.queue import TaskQueue
from app.worker.executor import WorkerExecutor


def run_worker(poll_interval: float = 0.5) -> None:
    queue = TaskQueue()
    while True:
        message = queue.dequeue()
        if message is None:
            time.sleep(poll_interval)
            continue
        with session_scope() as session:
            executor = WorkerExecutor(
                task_repository=TaskRepository(session),
                training_log_repository=TrainingLogRepository(session),
                event_stream=EventStream(),
                task_control=TaskControl(),
            )
            executor.execute(message)


if __name__ == "__main__":
    run_worker()
