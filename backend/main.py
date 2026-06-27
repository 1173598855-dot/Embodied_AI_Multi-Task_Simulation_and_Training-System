from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import tasks, training, ws
from worker.task_worker import TaskWorker
from worker.redis_queue import TaskQueue
from db.database import init_db
from config import REDIS_URL


worker: TaskWorker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker
    init_db()
    queue = TaskQueue(redis_url=REDIS_URL)
    worker = TaskWorker(queue)
    worker.start()
    yield
    if worker:
        worker.running = False


app = FastAPI(title="Embodied AI Training Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(ws.router, tags=["websocket"])