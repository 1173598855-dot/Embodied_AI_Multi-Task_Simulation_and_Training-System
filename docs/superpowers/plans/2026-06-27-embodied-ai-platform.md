# Embodied AI Platform — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-task embodied AI training platform with Q-learning agents running in Gym environments, task queue via Redis, and real-time training visualization.

**Architecture:** FastAPI backend with an embedded Worker thread consuming a Redis task queue. SQLAlchemy + MySQL for persistence. Vue 3 + Element Plus frontend with WebSocket-driven ECharts training curves. Docker Compose for 4-container deployment.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Redis, MySQL 8.0, Vue 3, Element Plus, ECharts, Pinia, Docker Compose

## Global Constraints

- Python >= 3.11, Node.js >= 20
- No external RL libraries (Stable-Baselines3 etc.) — hand-written Q-learning only
- PyBullet environment is skeleton-only (NotImplementedError)
- Crawler module is scope-excluded; only MySQL tasks + training_logs tables
- All code follows existing project style: clean, modular, meaningful names

## File Map

| File | Responsibility |
|------|---------------|
| `docker-compose.yml` | 4-service orchestration |
| `.env.example` | Environment variable template |
| `backend/Dockerfile` | Python container build |
| `backend/requirements.txt` | Python dependencies |
| `backend/config.py` | Settings from env vars |
| `backend/main.py` | FastAPI entry + Worker startup |
| `backend/db/database.py` | SQLAlchemy engine + session |
| `backend/db/models.py` | Task, TrainingLog ORM models |
| `backend/db/schemas.py` | Pydantic request/response schemas |
| `backend/api/deps.py` | FastAPI dependency injection |
| `backend/api/routes/tasks.py` | Task CRUD endpoints |
| `backend/api/routes/training.py` | Training start/pause/logs |
| `backend/api/routes/ws.py` | WebSocket reward stream |
| `backend/core/agent/base.py` | BaseAgent ABC |
| `backend/core/agent/q_learning.py` | QLearningAgent |
| `backend/core/environment/base.py` | BaseEnvironment ABC |
| `backend/core/environment/gym_env.py` | Gymnasium adapter |
| `backend/core/environment/pybullet_env.py` | PyBullet skeleton |
| `backend/core/trainer.py` | Training loop |
| `backend/worker/redis_queue.py` | Redis queue operations |
| `backend/worker/task_worker.py` | Background worker thread |
| `frontend/Dockerfile` | Node build + nginx serve |
| `frontend/nginx.conf` | Static + reverse proxy |
| `frontend/package.json` | Vue 3 dependencies |
| `frontend/src/main.js` | Vue app entry |
| `frontend/src/App.vue` | Root layout |
| `frontend/src/router/index.js` | Route definitions |
| `frontend/src/api/index.js` | Axios HTTP client |
| `frontend/src/stores/training.js` | Pinia + WebSocket state |
| `frontend/src/views/Dashboard.vue` | Overview dashboard |
| `frontend/src/views/TaskList.vue` | Task management |
| `frontend/src/views/Training.vue` | Training monitor |
| `frontend/src/views/Logs.vue` | Log viewer |
| `frontend/src/components/TaskForm.vue` | Create task dialog |
| `frontend/src/components/RewardChart.vue` | ECharts reward curve |
| `frontend/src/components/StepChart.vue` | ECharts step curve |


---

## Task 1: Project Scaffolding

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `frontend/Dockerfile`
- Create: `frontend/nginx.conf`

**Produces:** All 4 containers defined; backend and frontend have build files.

- [ ] **Step 1: Create directory structure**

```powershell
$dirs = @("backend/api/routes","backend/core/agent","backend/core/environment","backend/worker","backend/db","frontend/src/router","frontend/src/views","frontend/src/components","frontend/src/api","frontend/src/stores","frontend/public")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
```

- [ ] **Step 2: Create `.env.example`**

```
MYSQL_ROOT_PASSWORD=root123
MYSQL_DATABASE=embodied_ai
DATABASE_URL=mysql+aiomysql://root:root123@mysql:3306/embodied_ai
REDIS_URL=redis://redis:6379
```

- [ ] **Step 3: Create `docker-compose.yml`**

```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root123}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-embodied_ai}
    ports: ["3306:3306"]
    volumes: [mysql_data:/var/lib/mysql]
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on:
      mysql: { condition: service_healthy }
      redis: { condition: service_healthy }
    environment:
      DATABASE_URL: ${DATABASE_URL:-mysql+aiomysql://root:root123@mysql:3306/embodied_ai}
      REDIS_URL: ${REDIS_URL:-redis://redis:6379}
  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]
volumes:
  mysql_data:
```

- [ ] **Step 4: Create `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 5: Create `backend/requirements.txt`**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
aiomysql==0.2.0
pymysql==1.1.1
redis==5.2.1
pydantic==2.10.4
gymnasium==1.0.0
numpy==2.2.1
websockets==14.1
python-dotenv==1.0.1
```

- [ ] **Step 6: Create `backend/config.py`**

```python
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/embodied_ai")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
```

- [ ] **Step 7: Create `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

- [ ] **Step 8: Create `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    location / { root /usr/share/nginx/html; try_files $uri $uri/ /index.html; }
    location /api/ { proxy_pass http://backend:8000/api/; }
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

- [ ] **Step 9: Initialize git and commit**

```bash
git init && git add . && git commit -m "chore: project scaffolding with Docker Compose"
```


---

## Task 2: Database Layer

**Files:**
- Create: `backend/db/__init__.py`
- Create: `backend/db/database.py`
- Create: `backend/db/models.py`
- Create: `backend/db/schemas.py`

**Interfaces:**
- Produces: `SessionLocal`, `Task` model, `TrainingLog` model, `TaskCreate`/`TaskResponse`/`TrainingLogResponse` Pydantic schemas

- [ ] **Step 1: Create `backend/db/__init__.py`** (empty file)

- [ ] **Step 2: Create `backend/db/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 3: Create `backend/db/models.py`**

```python
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    env_type = Column(String(32), nullable=False, default="gym")
    env_name = Column(String(64), nullable=False, default="CartPole-v1")
    algo = Column(String(32), nullable=False, default="q_learning")
    status = Column(String(16), nullable=False, default="pending")
    config = Column(JSON, nullable=True)
    total_reward = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    logs = relationship("TrainingLog", back_populates="task", cascade="all, delete-orphan")

class TrainingLog(Base):
    __tablename__ = "training_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    episode = Column(Integer, nullable=False)
    step = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    avg_reward = Column(Float, nullable=True)
    state_snapshot = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    task = relationship("Task", back_populates="logs")
```

- [ ] **Step 4: Create `backend/db/schemas.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    name: str
    env_type: str = "gym"
    env_name: str = "CartPole-v1"
    algo: str = "q_learning"
    config: dict | None = None

class TaskResponse(BaseModel):
    id: int
    name: str
    env_type: str
    env_name: str
    algo: str
    status: str
    config: dict | None = None
    total_reward: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}

class TrainingLogResponse(BaseModel):
    id: int
    task_id: int
    episode: int
    step: int
    reward: float
    avg_reward: float | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}
```

- [ ] **Step 5: Create all `__init__.py` files**

```powershell
$pkgs = @("backend/api/__init__.py","backend/api/routes/__init__.py","backend/core/__init__.py","backend/core/agent/__init__.py","backend/core/environment/__init__.py","backend/worker/__init__.py")
foreach ($f in $pkgs) { New-Item -ItemType File -Path $f -Force | Out-Null }
```

- [ ] **Step 6: Commit**

```bash
git add . && git commit -m "feat: database layer with Task and TrainingLog models"
```


---

## Task 3: Core — Agent

**Files:**
- Create: `backend/core/agent/base.py`
- Create: `backend/core/agent/q_learning.py`

**Interfaces:**
- Produces: `BaseAgent` ABC with `choose_action(state) -> int`, `update(state, action, reward, next_state, done)`, `save(path)`, `load(path)`; `QLearningAgent(state_size, action_size, lr, gamma, epsilon, epsilon_decay, epsilon_min)`

- [ ] **Step 1: Create `backend/core/agent/base.py`**

```python
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def choose_action(self, state: int) -> int: ...

    @abstractmethod
    def update(self, state: int, action: int, reward: float, next_state: int, done: bool): ...

    @abstractmethod
    def save(self, path: str): ...

    @abstractmethod
    def load(self, path: str): ...
```

- [ ] **Step 2: Create `backend/core/agent/q_learning.py`**

```python
import numpy as np
from core.agent.base import BaseAgent

class QLearningAgent(BaseAgent):
    def __init__(self, state_size: int, action_size: int, lr: float = 0.1, gamma: float = 0.99,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995, epsilon_min: float = 0.01):
        self.q_table = np.zeros((state_size, action_size))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def choose_action(self, state: int) -> int:
        state = min(state, self.q_table.shape[0] - 1)
        if np.random.random() < self.epsilon:
            return np.random.randint(self.q_table.shape[1])
        return int(np.argmax(self.q_table[state]))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        state = min(state, self.q_table.shape[0] - 1)
        next_state = min(next_state, self.q_table.shape[0] - 1)
        target = reward + (0 if done else self.gamma * np.max(self.q_table[next_state]))
        self.q_table[state][action] += self.lr * (target - self.q_table[state][action])
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str):
        np.save(path, self.q_table)

    def load(self, path: str):
        self.q_table = np.load(path)
```

- [ ] **Step 3: Commit**

```bash
git add . && git commit -m "feat: BaseAgent ABC and QLearningAgent implementation"
```


---

## Task 4: Core — Environment

**Files:**
- Create: `backend/core/environment/base.py`
- Create: `backend/core/environment/gym_env.py`
- Create: `backend/core/environment/pybullet_env.py`
- Modify: `backend/core/environment/__init__.py` (add EnvFactory)

**Interfaces:**
- Produces: `BaseEnvironment` ABC, `GymEnvironment(env_name)`, `PyBulletEnvironment(urdf_path)` (NotImplementedError), `EnvFactory.create(env_type, env_name)`

- [ ] **Step 1: Create `backend/core/environment/base.py`**

```python
from abc import ABC, abstractmethod

class BaseEnvironment(ABC):
    @abstractmethod
    def reset(self) -> int: ...

    @abstractmethod
    def step(self, action: int) -> tuple[int, float, bool, dict]: ...

    @abstractmethod
    def action_space_size(self) -> int: ...

    @abstractmethod
    def state_space_size(self) -> int: ...
```

- [ ] **Step 2: Create `backend/core/environment/gym_env.py`**

```python
import gymnasium as gym
import numpy as np
from core.environment.base import BaseEnvironment

class GymEnvironment(BaseEnvironment):
    DISCRETE_BINS = 512

    def __init__(self, env_name: str = "CartPole-v1"):
        self.env = gym.make(env_name)
        self.env_name = env_name

    def _discretize(self, state) -> int:
        if isinstance(state, (int, np.integer)):
            return int(state)
        return hash(state.tobytes()) % self.DISCRETE_BINS

    def reset(self) -> int:
        state, _ = self.env.reset()
        return self._discretize(state)

    def step(self, action: int) -> tuple[int, float, bool, dict]:
        state, reward, terminated, truncated, info = self.env.step(action)
        return self._discretize(state), reward, terminated or truncated, info

    def action_space_size(self) -> int:
        return self.env.action_space.n

    def state_space_size(self) -> int:
        if hasattr(self.env.observation_space, "n"):
            return self.env.observation_space.n
        return self.DISCRETE_BINS
```

- [ ] **Step 3: Create `backend/core/environment/pybullet_env.py`**

```python
from core.environment.base import BaseEnvironment

class PyBulletEnvironment(BaseEnvironment):
    def __init__(self, urdf_path: str = None):
        raise NotImplementedError("PyBullet environment is not yet implemented")
    def reset(self) -> int:
        raise NotImplementedError
    def step(self, action: int) -> tuple[int, float, bool, dict]:
        raise NotImplementedError
    def action_space_size(self) -> int:
        raise NotImplementedError
    def state_space_size(self) -> int:
        raise NotImplementedError
```

- [ ] **Step 4: Create `backend/core/environment/__init__.py` with EnvFactory**

```python
from core.environment.base import BaseEnvironment
from core.environment.gym_env import GymEnvironment
from core.environment.pybullet_env import PyBulletEnvironment

class EnvFactory:
    @staticmethod
    def create(env_type: str, env_name: str = None) -> BaseEnvironment:
        if env_type == "gym":
            return GymEnvironment(env_name or "CartPole-v1")
        elif env_type == "robot":
            return PyBulletEnvironment(env_name)
        raise ValueError(f"Unknown env_type: {env_type}")
```

- [ ] **Step 5: Commit**

```bash
git add . && git commit -m "feat: BaseEnvironment, GymEnvironment, PyBullet skeleton, EnvFactory"
```


---

## Task 5: Core — Trainer

**Files:**
- Create: `backend/core/trainer.py`

**Interfaces:**
- Consumes: `BaseAgent` (choose_action, update), `BaseEnvironment` (reset, step)
- Produces: `Trainer(agent, env, task_id).run(episodes, callback)` where callback = `(task_id, episode, total_reward, epsilon) -> None`

- [ ] **Step 1: Create `backend/core/trainer.py`**

```python
from core.agent.base import BaseAgent
from core.environment.base import BaseEnvironment

class Trainer:
    def __init__(self, agent: BaseAgent, env: BaseEnvironment, task_id: int):
        self.agent = agent
        self.env = env
        self.task_id = task_id

    def run(self, episodes: int = 500, callback=None):
        for ep in range(episodes):
            state = self.env.reset()
            total_reward = 0.0
            while True:
                action = self.agent.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                self.agent.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                if done:
                    break
            if callback:
                callback(self.task_id, ep, total_reward, self.agent.epsilon)
```

- [ ] **Step 2: Commit**

```bash
git add . && git commit -m "feat: Trainer training loop with callback support"
```


---

## Task 6: Worker — Redis Queue + Task Worker

**Files:**
- Create: `backend/worker/redis_queue.py`
- Create: `backend/worker/task_worker.py`

**Interfaces:**
- Consumes: `Trainer`, `EnvFactory`, `QLearningAgent`, `SessionLocal`, `Task`, `TrainingLog`
- Produces: `TaskQueue(redis_url)` with push/pop/size/update_status/push_reward_stream; `TaskWorker(queue)` with start()

- [ ] **Step 1: Create `backend/worker/redis_queue.py`**

```python
import json
import redis

class TaskQueue:
    QUEUE_KEY = "task_queue"

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.Redis.from_url(redis_url)

    def push(self, task_id: int):
        self.redis_client.lpush(self.QUEUE_KEY, task_id)

    def pop(self) -> int | None:
        raw = self.redis_client.rpop(self.QUEUE_KEY)
        return int(raw) if raw else None

    def size(self) -> int:
        return self.redis_client.llen(self.QUEUE_KEY)

    def update_status(self, task_id: int, data: dict):
        self.redis_client.set(f"task:{task_id}:status", json.dumps(data), ex=1800)

    def push_reward_stream(self, task_id: int, episode: int, reward: float, epsilon: float):
        self.redis_client.xadd(
            f"task:{task_id}:reward_stream",
            {"episode": str(episode), "reward": str(reward), "epsilon": str(epsilon)},
            maxlen=5000,
        )
```

- [ ] **Step 2: Create `backend/worker/task_worker.py`**

```python
import threading
import time
import logging
from core.trainer import Trainer
from core.environment import EnvFactory
from core.agent.q_learning import QLearningAgent
from worker.redis_queue import TaskQueue
from db.database import SessionLocal
from db.models import Task, TrainingLog

logger = logging.getLogger(__name__)

class TaskWorker:
    def __init__(self, queue: TaskQueue):
        self.queue = queue
        self.running = True
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("TaskWorker started")

    def _run(self):
        while self.running:
            task_id = self.queue.pop()
            if task_id is not None:
                self._execute(task_id)
            else:
                time.sleep(0.5)

    def _execute(self, task_id: int):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            task.status = "running"
            db.commit()
            self.queue.update_status(task_id, {"status": "running"})

            env = EnvFactory.create(task.env_type, task.env_name)
            agent = QLearningAgent(state_size=env.state_space_size(), action_size=env.action_space_size())

            if task.config:
                agent.lr = task.config.get("lr", agent.lr)
                agent.gamma = task.config.get("gamma", agent.gamma)
                agent.epsilon = task.config.get("epsilon", agent.epsilon)

            config = task.config or {}
            episodes = config.get("episodes", 500)
            last_reward = 0.0

            def on_episode_done(tid, episode, reward, epsilon):
                nonlocal last_reward
                last_reward = reward
                db.add(TrainingLog(task_id=tid, episode=episode, step=episode, reward=reward))
                db.commit()
                self.queue.push_reward_stream(tid, episode, reward, epsilon)

            trainer = Trainer(agent, env, task_id)
            trainer.run(episodes=episodes, callback=on_episode_done)

            task.status = "completed"
            task.total_reward = last_reward
            db.commit()
            self.queue.update_status(task_id, {"status": "completed"})
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = "failed"
                    db.commit()
                self.queue.update_status(task_id, {"status": "failed", "error": str(e)})
            except Exception:
                pass
        finally:
            db.close()
```

- [ ] **Step 3: Commit**

```bash
git add . && git commit -m "feat: Redis task queue and background worker thread"
```


---

## Task 7: API Layer

**Files:**
- Create: `backend/api/deps.py`
- Create: `backend/api/routes/tasks.py`
- Create: `backend/api/routes/training.py`
- Create: `backend/api/routes/ws.py`
- Create: `backend/main.py`

**Interfaces:**
- Consumes: `SessionLocal`, `TaskQueue`, `TaskWorker`, all DB models and schemas
- Produces: FastAPI app with routes at `/api/tasks`, `/api/training`, `/ws/{task_id}`

- [ ] **Step 1: Create `backend/api/deps.py`**

```python
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
```

- [ ] **Step 2: Create `backend/api/routes/tasks.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_queue
from db.models import Task
from db.schemas import TaskCreate, TaskResponse

router = APIRouter()

@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).all()

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db)):
    task = Task(name=body.name, env_type=body.env_type, env_name=body.env_name, algo=body.algo, config=body.config)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
```

- [ ] **Step 3: Create `backend/api/routes/training.py`**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_queue
from db.models import Task, TrainingLog
from db.schemas import TrainingLogResponse
from worker.redis_queue import TaskQueue

router = APIRouter()

@router.post("/{task_id}/start")
def start_training(task_id: int, db: Session = Depends(get_db), queue: TaskQueue = Depends(get_queue)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "running":
        raise HTTPException(status_code=400, detail="Task is already running")
    task.status = "pending"
    db.commit()
    queue.push(task_id)
    return {"message": "Task queued", "task_id": task_id}

@router.post("/{task_id}/pause")
def pause_training(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "paused"
    db.commit()
    return {"message": "Task paused", "task_id": task_id}

@router.get("/{task_id}/logs", response_model=list[TrainingLogResponse])
def get_training_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(TrainingLog).filter(TrainingLog.task_id == task_id).order_by(TrainingLog.episode).all()
```

- [ ] **Step 4: Create `backend/api/routes/ws.py`**

```python
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from config import REDIS_URL
import redis

router = APIRouter()

@router.websocket("/ws/{task_id}")
async def websocket_reward_stream(websocket: WebSocket, task_id: int):
    await websocket.accept()
    r = redis.Redis.from_url(REDIS_URL)
    stream_key = f"task:{task_id}:reward_stream"
    last_id = "0"
    try:
        while True:
            entries = r.xread({stream_key: last_id}, count=10, block=2000)
            if entries:
                for _stream_name, messages in entries:
                    for msg_id, fields in messages:
                        last_id = msg_id
                        await websocket.send_json({
                            "type": "reward_update",
                            "episode": int(fields.get(b"episode", fields.get("episode", 0))),
                            "reward": float(fields.get(b"reward", fields.get("reward", 0))),
                            "epsilon": float(fields.get(b"epsilon", fields.get("epsilon", 0))),
                        })
            else:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        r.close()
```

- [ ] **Step 5: Create `backend/main.py`**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import tasks, training, ws
from worker.task_worker import TaskWorker
from worker.redis_queue import TaskQueue
from db.database import init_db
from config import REDIS_URL

worker = None

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

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(ws.router, tags=["websocket"])
```

- [ ] **Step 6: Commit**

```bash
git add . && git commit -m "feat: FastAPI routes, WebSocket, and app entry point"
```


---

## Task 8: Frontend — Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/api/index.js`
- Create: `frontend/src/stores/training.js`
- Create: placeholder view files

**Interfaces:**
- Produces: Vue 3 app with Element Plus, Vue Router (4 routes), Pinia store, Axios client

- [ ] **Step 1: Create `frontend/package.json`**

```json
{
  "name": "embodied-ai-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "pinia": "^2.3.0",
    "element-plus": "^2.9.1",
    "axios": "^1.7.9",
    "echarts": "^5.5.1",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^6.0.5"
  }
}
```

- [ ] **Step 2: Create `frontend/vite.config.js`**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
})
```

- [ ] **Step 3: Create `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Embodied AI Training Platform</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create `frontend/src/main.js`**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

- [ ] **Step 5: Create `frontend/src/App.vue`**

```vue
<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background-color: #304156">
      <div style="padding: 20px; color: #fff; font-size: 16px; font-weight: bold; text-align: center">
        AI 训练平台
      </div>
      <el-menu :default-active="$route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff">
        <el-menu-item index="/"><span>仪表盘</span></el-menu-item>
        <el-menu-item index="/tasks"><span>任务管理</span></el-menu-item>
        <el-menu-item index="/logs"><span>训练日志</span></el-menu-item>
      </el-menu>
    </el-aside>
    <el-main style="padding: 20px; background-color: #f5f7fa">
      <router-view />
    </el-main>
  </el-container>
</template>
<script setup></script>
<style>body { margin: 0; }</style>
```

- [ ] **Step 6: Create `frontend/src/router/index.js`**

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/tasks', name: 'Tasks', component: () => import('../views/TaskList.vue') },
  { path: '/training/:id', name: 'Training', component: () => import('../views/Training.vue') },
  { path: '/logs', name: 'Logs', component: () => import('../views/Logs.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
```

- [ ] **Step 7: Create placeholder view files**

Create minimal `<template><div>Page Name</div></template>` for Dashboard.vue, TaskList.vue, Training.vue, Logs.vue.

- [ ] **Step 8: Create `frontend/src/api/index.js`**

```javascript
import axios from 'axios'
const api = axios.create({ baseURL: '/api', timeout: 10000 })
export default api
```

- [ ] **Step 9: Create `frontend/src/stores/training.js`**

```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTrainingStore = defineStore('training', () => {
  const rewardData = ref([])
  const taskStatus = ref('pending')
  let ws = null

  function connect(taskId) {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    ws = new WebSocket(`${protocol}//${location.host}/ws/${taskId}`)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'reward_update') {
        rewardData.value.push({ episode: data.episode, reward: data.reward, epsilon: data.epsilon })
      } else if (data.type === 'status_change') {
        taskStatus.value = data.status
      }
    }
    ws.onclose = () => { ws = null }
  }

  function disconnect() { if (ws) { ws.close(); ws = null } }
  function clearData() { rewardData.value = []; taskStatus.value = 'pending' }

  return { rewardData, taskStatus, connect, disconnect, clearData }
})
```

- [ ] **Step 10: Commit**

```bash
git add . && git commit -m "feat: Vue 3 frontend scaffolding with router, stores, layout"
```


---

## Task 9: Frontend — Views & Components

**Files:**
- Create: `frontend/src/components/TaskForm.vue`
- Create: `frontend/src/components/RewardChart.vue`
- Create: `frontend/src/components/StepChart.vue`
- Replace: `frontend/src/views/Dashboard.vue`
- Replace: `frontend/src/views/TaskList.vue`
- Replace: `frontend/src/views/Training.vue`
- Replace: `frontend/src/views/Logs.vue`

**Interfaces:**
- Consumes: `api/index.js` (axios), `stores/training.js` (Pinia store)
- Produces: Complete UI with dashboard stats, task CRUD, real-time training charts, log viewer

- [ ] **Step 1: Create `frontend/src/components/TaskForm.vue`**

```vue
<template>
  <el-dialog v-model="visible" title="创建训练任务" width="500px" @close="$emit('close')">
    <el-form :model="form" label-width="100px">
      <el-form-item label="任务名称">
        <el-input v-model="form.name" placeholder="如: CartPole 训练" />
      </el-form-item>
      <el-form-item label="环境类型">
        <el-select v-model="form.env_type" style="width: 100%">
          <el-option label="Gym" value="gym" />
          <el-option label="PyBullet (机器人)" value="robot" disabled />
        </el-select>
      </el-form-item>
      <el-form-item label="环境名称">
        <el-input v-model="form.env_name" placeholder="如: CartPole-v1" />
      </el-form-item>
      <el-form-item label="训练轮数">
        <el-input-number v-model="form.config.episodes" :min="10" :max="10000" />
      </el-form-item>
      <el-form-item label="学习率">
        <el-input-number v-model="form.config.lr" :min="0.001" :max="1.0" :step="0.01" />
      </el-form-item>
      <el-form-item label="折扣因子">
        <el-input-number v-model="form.config.gamma" :min="0.1" :max="1.0" :step="0.01" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="submit" :loading="loading">创建</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, reactive } from 'vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['close', 'created'])
const visible = ref(props.show)
const loading = ref(false)
const form = reactive({
  name: '', env_type: 'gym', env_name: 'CartPole-v1', algo: 'q_learning',
  config: { episodes: 500, lr: 0.1, gamma: 0.99, epsilon: 1.0 },
})

async function submit() {
  if (!form.name) { ElMessage.warning('请输入任务名称'); return }
  loading.value = true
  try {
    await api.post('/tasks', form)
    ElMessage.success('任务创建成功')
    emit('created')
    emit('close')
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
  } finally { loading.value = false }
}
</script>
```

- [ ] **Step 2: Create `frontend/src/components/RewardChart.vue`**

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 400px"></div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ data: { type: Array, default: () => [] } })
const chartRef = ref(null)
let chart = null

onMounted(() => { chart = echarts.init(chartRef.value); updateChart(); window.addEventListener('resize', () => chart?.resize()) })
onUnmounted(() => { chart?.dispose() })
watch(() => props.data, updateChart, { deep: true })

function updateChart() {
  if (!chart) return
  const episodes = props.data.map(d => d.episode)
  const rewards = props.data.map(d => d.reward)
  const avgRewards = rewards.map((_, i) => {
    const start = Math.max(0, i - 19)
    return rewards.slice(start, i + 1).reduce((a, b) => a + b, 0) / (i - start + 1)
  })
  chart.setOption({
    title: { text: 'Reward 曲线', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['Reward', 'Average (20)'] },
    xAxis: { type: 'category', data: episodes, name: 'Episode' },
    yAxis: { type: 'value', name: 'Reward' },
    series: [
      { name: 'Reward', type: 'scatter', data: rewards, symbolSize: 3, itemStyle: { color: '#409eff' } },
      { name: 'Average (20)', type: 'line', data: avgRewards, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
    ],
    grid: { left: 60, right: 20, top: 40, bottom: 50 },
  })
}
</script>
```

- [ ] **Step 3: Create `frontend/src/components/StepChart.vue`**

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 300px"></div>
</template>
<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ data: { type: Array, default: () => [] } })
const chartRef = ref(null)
let chart = null

onMounted(() => { chart = echarts.init(chartRef.value); updateChart(); window.addEventListener('resize', () => chart?.resize()) })
onUnmounted(() => { chart?.dispose() })
watch(() => props.data, updateChart, { deep: true })

function updateChart() {
  if (!chart) return
  chart.setOption({
    title: { text: 'Epsilon 衰减', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.data.map(d => d.episode), name: 'Episode' },
    yAxis: { type: 'value', name: 'Epsilon', max: 1.0 },
    series: [{ type: 'line', data: props.data.map(d => d.epsilon), smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { color: 'rgba(103,194,58,0.1)' } }],
    grid: { left: 60, right: 20, top: 40, bottom: 40 },
  })
}
</script>
```

- [ ] **Step 4: Replace `frontend/src/views/Dashboard.vue`**

```vue
<template>
  <div>
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6"><el-card shadow="hover"><template #header>任务总数</template><div style="font-size: 32px; font-weight: bold">{{ stats.total }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><template #header>运行中</template><div style="font-size: 32px; font-weight: bold; color: #409eff">{{ stats.running }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><template #header>已完成</template><div style="font-size: 32px; font-weight: bold; color: #67c23a">{{ stats.completed }}</div></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><template #header>失败</template><div style="font-size: 32px; font-weight: bold; color: #f56c6c">{{ stats.failed }}</div></el-card></el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'
const stats = ref({ total: 0, running: 0, completed: 0, failed: 0 })
onMounted(async () => {
  try {
    const { data } = await api.get('/tasks')
    stats.value.total = data.length
    stats.value.running = data.filter(t => t.status === 'running').length
    stats.value.completed = data.filter(t => t.status === 'completed').length
    stats.value.failed = data.filter(t => t.status === 'failed').length
  } catch (e) { console.error('Failed to load stats', e) }
})
</script>
```

- [ ] **Step 5: Replace `frontend/src/views/TaskList.vue`**

```vue
<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h2>任务管理</h2>
      <el-button type="primary" @click="showForm = true">新建任务</el-button>
    </div>
    <el-table :data="tasks" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="env_type" label="环境" width="100" />
      <el-table-column prop="env_name" label="环境名" width="140" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }"><el-tag :type="statusType(row.status)">{{ row.status }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="total_reward" label="总Reward" width="100" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="startTask(row.id)" :disabled="row.status === 'running'">启动</el-button>
          <el-button size="small" @click="$router.push('/training/' + row.id)">监控</el-button>
          <el-popconfirm title="确认删除?" @confirm="deleteTask(row.id)">
            <template #reference><el-button size="small" type="danger">删除</el-button></template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <TaskForm v-if="showForm" :show="showForm" @close="showForm = false" @created="loadTasks" />
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'
import TaskForm from '../components/TaskForm.vue'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const showForm = ref(false)
const statusType = (s) => ({ pending: 'info', running: '', completed: 'success', paused: 'warning', failed: 'danger' }[s] || 'info')

async function loadTasks() { try { const { data } = await api.get('/tasks'); tasks.value = data } catch { ElMessage.error('加载任务失败') } }
async function startTask(id) { try { await api.post('/training/' + id + '/start'); ElMessage.success('任务已入队'); loadTasks() } catch (e) { ElMessage.error(e.response?.data?.detail || '启动失败') } }
async function deleteTask(id) { try { await api.delete('/tasks/' + id); ElMessage.success('已删除'); loadTasks() } catch { ElMessage.error('删除失败') } }

onMounted(loadTasks)
</script>
```

- [ ] **Step 6: Replace `frontend/src/views/Training.vue`**

```vue
<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h2>训练监控 — 任务 #{{ taskId }}</h2>
      <el-tag :type="statusType(store.taskStatus)" size="large">{{ store.taskStatus }}</el-tag>
    </div>
    <el-empty v-if="store.rewardData.length === 0" description="等待训练数据..." />
    <template v-else>
      <el-card shadow="never" style="margin-bottom: 16px"><RewardChart :data="store.rewardData" /></el-card>
      <el-card shadow="never"><StepChart :data="store.rewardData" /></el-card>
    </template>
  </div>
</template>
<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTrainingStore } from '../stores/training.js'
import RewardChart from '../components/RewardChart.vue'
import StepChart from '../components/StepChart.vue'

const route = useRoute()
const store = useTrainingStore()
const taskId = computed(() => route.params.id)
const statusType = (s) => ({ pending: 'info', running: '', completed: 'success', failed: 'danger' }[s] || 'info')

onMounted(() => { store.clearData(); store.connect(taskId.value) })
onUnmounted(() => { store.disconnect() })
</script>
```

- [ ] **Step 7: Replace `frontend/src/views/Logs.vue`**

```vue
<template>
  <div>
    <h2>训练日志</h2>
    <el-select v-model="selectedTaskId" placeholder="选择任务" style="width: 240px; margin-bottom: 16px" @change="loadLogs">
      <el-option v-for="t in tasks" :key="t.id" :label="t.id + ' - ' + t.name" :value="t.id" />
    </el-select>
    <el-table :data="logs" stripe style="width: 100%">
      <el-table-column prop="episode" label="Episode" width="100" />
      <el-table-column prop="reward" label="Reward" width="120" />
      <el-table-column prop="created_at" label="时间">
        <template #default="{ row }">{{ row.created_at ? new Date(row.created_at).toLocaleString() : '' }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const tasks = ref([])
const logs = ref([])
const selectedTaskId = ref(null)

async function loadLogs() {
  if (!selectedTaskId.value) return
  const { data } = await api.get('/training/' + selectedTaskId.value + '/logs')
  logs.value = data
}

onMounted(async () => { const { data } = await api.get('/tasks'); tasks.value = data })
</script>
```

- [ ] **Step 8: Commit**

```bash
git add . && git commit -m "feat: frontend views and components — dashboard, task management, training charts, logs"
```


---

## Task 10: Integration Verification

**Files:** No new files — verification only.

- [ ] **Step 1: Build frontend locally**

```powershell
cd frontend; npm install; npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 2: Verify Python imports**

```powershell
cd backend; python -c "from core.agent.q_learning import QLearningAgent; from core.environment import EnvFactory; from core.trainer import Trainer; from worker.redis_queue import TaskQueue; print('All imports OK')"
```

Expected: `All imports OK`

- [ ] **Step 3: Docker Compose build test**

```powershell
docker-compose build
```

Expected: All 4 services build without errors.

- [ ] **Step 4: Final commit if any fixes needed**

```bash
git add . && git commit -m "fix: integration verification fixes"
```
