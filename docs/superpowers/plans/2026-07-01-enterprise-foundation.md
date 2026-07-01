# Enterprise Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the existing embodied AI training prototype into an enterprise-grade foundation with a modular backend, independent worker process, migrations, unified errors, health checks, and compatible frontend updates.

**Architecture:** Use a modular monolith backend under `backend/app/`. The FastAPI API process exposes REST, WebSocket, and health endpoints only; an independent worker process consumes Redis queue messages and executes training. Shared domain rules, application services, database repositories, Redis protocols, and training code keep behavior consistent without prematurely splitting into microservices.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic, Redis, MySQL 8.0, Gymnasium, NumPy, Pydantic 2.x, Vue 3, Pinia, Element Plus, ECharts, Vite, Docker Compose.

## Global Constraints

- Preserve existing product behavior: task CRUD, training start/pause/cancel, Q-learning in Gymnasium, MySQL training logs, WebSocket reward curves, and Docker Compose local deployment.
- API startup must not launch an embedded worker.
- Worker startup must be an independent explicit process: `python -m app.worker.main`.
- API startup must be explicit: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Use Alembic migrations as the production-style schema path.
- Keep PyBullet as a skeleton-only environment.
- Do not add login, JWT, roles, multi-tenancy, PPO, Kubernetes, Prometheus, or Grafana in this phase.
- Keep frontend scope to compatibility, status/event updates, error handling, and Chinese text repair.
- Follow existing project style, keep edits focused, and avoid unrelated refactors.

---

## File Structure

### Backend Package
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/errors.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/app/core/lifecycle.py`
- Create: `backend/app/domain/task_state.py`
- Create: `backend/app/domain/task_rules.py`
- Create: `backend/app/domain/training_config.py`
- Create: `backend/app/application/task_service.py`
- Create: `backend/app/application/training_log_service.py`
- Create: `backend/app/infrastructure/db/database.py`
- Create: `backend/app/infrastructure/db/models.py`
- Create: `backend/app/infrastructure/db/repositories.py`
- Create: `backend/app/infrastructure/redis/queue.py`
- Create: `backend/app/infrastructure/redis/events.py`
- Create: `backend/app/infrastructure/redis/control.py`
- Create: `backend/app/training/agent/base.py`
- Create: `backend/app/training/agent/q_learning.py`
- Create: `backend/app/training/environment/base.py`
- Create: `backend/app/training/environment/gym_env.py`
- Create: `backend/app/training/environment/pybullet_env.py`
- Create: `backend/app/training/trainer.py`
- Create: `backend/app/worker/main.py`
- Create: `backend/app/worker/executor.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/api/routes/root.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/app/api/routes/tasks.py`
- Create: `backend/app/api/routes/training.py`
- Create: `backend/app/api/routes/ws.py`
- Add package markers: `backend/app/**/__init__.py` where needed.

### Migrations And Tests
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/versions/20260701_initial_enterprise_foundation.py`
- Create or replace focused tests under `backend/tests/` for domain, config, repositories, services, worker, API routes, health checks, and training loop control.

### Modified Existing Files
- Modify: `backend/Dockerfile`
- Modify: `backend/requirements.txt`
- Modify: `docker-compose.yml`
- Modify: `frontend/src/api/index.js`
- Modify: `frontend/src/stores/training.js`
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/views/TaskList.vue`
- Modify: `frontend/src/views/Training.vue`
- Modify: `frontend/src/views/Logs.vue`
- Modify: `frontend/src/components/TaskForm.vue`
- Modify: `frontend/nginx.conf` only if proxy paths need adjustment.

---

### Task 1: App Package, Settings, Logging

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/logging.py`
- Test: `backend/tests/test_config.py`

**Interfaces:**
- Produces: `settings` with `DATABASE_URL`, `REDIS_URL`, `TASK_QUEUE_KEY`, `EVENT_STREAM_MAXLEN`, `TASK_CONTROL_TTL`, `ENV`, `LOG_LEVEL`.
- Produces: `configure_logging(level: str | None, service: str) -> None`.
- Produces: `get_logger(service: str) -> logging.LoggerAdapter`.

- [ ] **Step 1: Write the failing config test**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings


def test_settings_defaults_are_enterprise_safe():
    assert settings.DATABASE_URL.startswith("mysql+pymysql://")
    assert settings.REDIS_URL.startswith("redis://")
    assert settings.TASK_QUEUE_KEY == "embodied_ai:task_queue"
    assert settings.EVENT_STREAM_MAXLEN == 5000
    assert settings.TASK_CONTROL_TTL == 3600
    assert settings.ENV in {"development", "test", "production"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest backend/tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`.

- [ ] **Step 3: Implement settings and logging**

```python
# backend/app/core/config.py
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:root123@localhost:3306/embodied_ai")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    TASK_QUEUE_KEY: str = os.getenv("TASK_QUEUE_KEY", "embodied_ai:task_queue")
    EVENT_STREAM_MAXLEN: int = int(os.getenv("EVENT_STREAM_MAXLEN", "5000"))
    TASK_CONTROL_TTL: int = int(os.getenv("TASK_CONTROL_TTL", "3600"))
    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG" if os.getenv("ENV", "development") == "development" else "INFO")


settings = Settings()
```

```python
# backend/app/core/logging.py
import logging


def configure_logging(level: str | None = None, service: str = "api") -> None:
    log_level = level or "INFO"
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s service=%(service)s request_id=%(request_id)s %(message)s",
    )


def get_logger(service: str = "api") -> logging.LoggerAdapter:
    logger = logging.getLogger(service)
    return logging.LoggerAdapter(logger, {"service": service, "request_id": "-"})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest backend/tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app backend/tests/test_config.py
git commit -m "feat: add app settings and logging foundation"
```

---

### Task 2: Domain State Rules And Training Config

**Files:**
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/task_state.py`
- Create: `backend/app/domain/task_rules.py`
- Create: `backend/app/domain/training_config.py`
- Test: `backend/tests/test_task_state.py`
- Test: `backend/tests/test_task_rules.py`
- Test: `backend/tests/test_training_config.py`

**Interfaces:**
- Produces: `TaskStatus(StrEnum)` values `created`, `queued`, `running`, `paused`, `completed`, `failed`, `canceled`.
- Produces: `ControlCommand(StrEnum)` values `pause`, `cancel`.
- Produces: `can_start`, `can_pause`, `can_cancel`, `can_delete`, `is_terminal`.
- Produces: `TrainingConfig` dataclass and `parse_training_config(payload: dict | None) -> TrainingConfig`.

- [ ] **Step 1: Write failing tests for state rules**

Test every state against start, pause, cancel, delete, and terminal predicates using explicit expected lists from the approved spec.

Run: `python -m pytest backend/tests/test_task_state.py backend/tests/test_task_rules.py backend/tests/test_training_config.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Implement domain modules**

```python
# backend/app/domain/task_state.py
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
```

```python
# backend/app/domain/task_rules.py
from app.domain.task_state import TaskStatus

STARTABLE = {TaskStatus.created, TaskStatus.paused, TaskStatus.failed}
PAUSABLE = {TaskStatus.queued, TaskStatus.running}
CANCELABLE = {TaskStatus.created, TaskStatus.queued, TaskStatus.running, TaskStatus.paused, TaskStatus.failed}
DELETABLE = {TaskStatus.created, TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}
TERMINAL = {TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}


def can_start(status: TaskStatus) -> bool:
    return status in STARTABLE


def can_pause(status: TaskStatus) -> bool:
    return status in PAUSABLE


def can_cancel(status: TaskStatus) -> bool:
    return status in CANCELABLE


def can_delete(status: TaskStatus) -> bool:
    return status in DELETABLE


def is_terminal(status: TaskStatus) -> bool:
    return status in TERMINAL
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_task_state.py backend/tests/test_task_rules.py backend/tests/test_training_config.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/domain backend/tests/test_task_state.py backend/tests/test_task_rules.py backend/tests/test_training_config.py
git commit -m "feat: add enterprise task state rules"
```

---

### Task 3: Database Models And Repositories

**Files:**
- Create: `backend/app/infrastructure/__init__.py`
- Create: `backend/app/infrastructure/db/__init__.py`
- Create: `backend/app/infrastructure/db/database.py`
- Create: `backend/app/infrastructure/db/models.py`
- Create: `backend/app/infrastructure/db/repositories.py`
- Test: `backend/tests/test_repositories.py`

**Interfaces:**
- Produces: SQLAlchemy `Base`, `engine`, `SessionLocal`, `session_scope()`.
- Produces: `TaskModel`, `TrainingLogModel` with `current_run_id`, `error_message`, and `run_id` fields.
- Produces: `TaskRepository` methods `create`, `get`, `list`, `delete`, `set_status`, `set_run`, `set_total_reward`, `set_error`.
- Produces: `TrainingLogRepository` methods `create`, `list_by_task`, `delete_by_task`.

- [ ] **Step 1: Write failing repository tests**

Use in-memory SQLite and `Base.metadata.create_all(test_engine)` inside tests. Cover task creation, list ordering, status updates, delete cascade, log creation, and log retrieval order.

Run: `python -m pytest backend/tests/test_repositories.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Implement models and repositories**

Keep DB concerns inside `app.infrastructure.db`. Do not import Redis or FastAPI here.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_repositories.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/infrastructure/db backend/tests/test_repositories.py
git commit -m "feat: add database models and repositories"
```

---

### Task 4: Redis Queue, Event Stream, Control Protocol

**Files:**
- Create: `backend/app/infrastructure/redis/__init__.py`
- Create: `backend/app/infrastructure/redis/queue.py`
- Create: `backend/app/infrastructure/redis/events.py`
- Create: `backend/app/infrastructure/redis/control.py`
- Modify: `backend/requirements.txt`
- Test: `backend/tests/test_redis_protocol.py`

**Interfaces:**
- Produces: `QueuedTaskMessage(task_id: int, run_id: str, attempt: int)`.
- Produces: `TaskQueue.enqueue(task_id: int, run_id: str, attempt: int = 1) -> None`.
- Produces: `TaskQueue.dequeue() -> QueuedTaskMessage | None`.
- Produces: `EventStream.publish(task_id: int, event: dict) -> None` and `read(task_id: int, last_id: str, count: int = 10, block_ms: int = 2000)`.
- Produces: `TaskControl.set_command`, `get_command`, `clear_command`.

- [ ] **Step 1: Add `fakeredis` test dependency**

Add `fakeredis==2.26.2` to `backend/requirements.txt` so Redis protocol tests do not require a live Redis server.

- [ ] **Step 2: Write failing Redis protocol tests**

Cover queue round-trip JSON, malformed message skip/failure behavior, event stream publish/read, and pause/cancel control command validation.

Run: `python -m pytest backend/tests/test_redis_protocol.py -v`
Expected: FAIL with import errors.

- [ ] **Step 3: Implement Redis modules**

Use key names from settings: queue key `embodied_ai:task_queue`, event stream `embodied_ai:task:{task_id}:events`, control key `embodied_ai:task:{task_id}:control`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest backend/tests/test_redis_protocol.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/infrastructure/redis backend/tests/test_redis_protocol.py backend/requirements.txt
git commit -m "feat: add Redis queue event and control protocol"
```

---

### Task 5: Training Core Migration

**Files:**
- Create: `backend/app/training/__init__.py`
- Create: `backend/app/training/agent/base.py`
- Create: `backend/app/training/agent/q_learning.py`
- Create: `backend/app/training/environment/base.py`
- Create: `backend/app/training/environment/gym_env.py`
- Create: `backend/app/training/environment/pybullet_env.py`
- Create: `backend/app/training/trainer.py`
- Test: `backend/tests/test_training_core.py`
- Test: `backend/tests/test_train_loop_control.py`

**Interfaces:**
- Produces: `QLearningAgent` preserving current behavior.
- Produces: `EnvFactory.create(env_type: str, env_name: str | None)`.
- Produces: `Trainer.run(episodes: int, on_episode=None, on_control=None) -> str | None`.

- [ ] **Step 1: Write failing training tests**

Cover Q-table shape, epsilon decay after done, Gym continuous-state discretization contract, PyBullet skeleton raising `NotImplementedError`, trainer pause/cancel callbacks.

Run: `python -m pytest backend/tests/test_training_core.py backend/tests/test_train_loop_control.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Move current training code into `app.training`**

Port from existing `backend/core/agent`, `backend/core/environment`, and `backend/core/trainer.py`. Keep behavior unchanged except callback names and run-id support required by the spec.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_training_core.py backend/tests/test_train_loop_control.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/training backend/tests/test_training_core.py backend/tests/test_train_loop_control.py
git commit -m "feat: migrate training core into app package"
```

---

### Task 6: Application Services

**Files:**
- Create: `backend/app/application/__init__.py`
- Create: `backend/app/application/task_service.py`
- Create: `backend/app/application/training_log_service.py`
- Test: `backend/tests/test_task_service.py`
- Test: `backend/tests/test_training_log_service.py`

**Interfaces:**
- Produces: `TaskService.create_task`, `get_task`, `list_tasks`, `delete_task`, `start_task`, `pause_task`, `cancel_task`.
- Produces: `TrainingLogService.list_logs(task_id: int)`.
- Consumes: domain rules, repositories, Redis queue, Redis control, Redis events.

- [ ] **Step 1: Write failing service tests with fakes**

Use in-memory fake repositories and fake queue/control objects. Cover allowed and rejected start/pause/cancel/delete transitions, queue message creation, control command creation, and log listing.

Run: `python -m pytest backend/tests/test_task_service.py backend/tests/test_training_log_service.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Implement service layer**

Services must raise application errors from Task 7 signatures once available. Until Task 7 lands, define narrow local errors and replace/import them when Task 7 is implemented.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_task_service.py backend/tests/test_training_log_service.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/application backend/tests/test_task_service.py backend/tests/test_training_log_service.py
git commit -m "feat: add task application services"
```

---

### Task 7: Errors, API App, Health Checks

**Files:**
- Create: `backend/app/core/errors.py`
- Create: `backend/app/core/lifecycle.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/api/routes/root.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_root.py`
- Test: `backend/tests/test_health.py`
- Test: `backend/tests/test_api_errors.py`

**Interfaces:**
- Produces: `AppError`, `NotFoundError`, `ConflictError`, `ValidationAppError`, `InfrastructureError`.
- Produces: unified error response `{"error": {"code": str, "message": str, "details": dict}}`.
- Produces: `GET /`, `GET /health/live`, `GET /health/ready`.
- Produces: `create_app() -> FastAPI` and module-level `app`.

- [ ] **Step 1: Write failing API foundation tests**

Cover root route, live route, ready route dependency override, and error envelope mapping for each app error type.

Run: `python -m pytest backend/tests/test_root.py backend/tests/test_health.py backend/tests/test_api_errors.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Implement app, dependencies, health, errors**

Do not start a worker in FastAPI lifespan. Readiness checks DB and Redis through injectable dependencies.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_root.py backend/tests/test_health.py backend/tests/test_api_errors.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/errors.py backend/app/core/lifecycle.py backend/app/api backend/app/main.py backend/tests/test_root.py backend/tests/test_health.py backend/tests/test_api_errors.py
git commit -m "feat: add API app errors and health checks"
```

---

### Task 8: REST And WebSocket Routes

**Files:**
- Create: `backend/app/api/routes/tasks.py`
- Create: `backend/app/api/routes/training.py`
- Create: `backend/app/api/routes/ws.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_tasks_api.py`
- Test: `backend/tests/test_training_api.py`

**Interfaces:**
- Produces: task CRUD endpoints under `/api/tasks`.
- Produces: training control endpoints under `/api/training/{task_id}`.
- Produces: training logs endpoint `/api/training/{task_id}/logs`.
- Produces: WebSocket `/ws/{task_id}` reading Redis Stream events.

- [ ] **Step 1: Write failing route tests**

Override app dependencies with fake services. Cover success and error response for list/create/get/delete/start/pause/cancel/logs.

Run: `python -m pytest backend/tests/test_tasks_api.py backend/tests/test_training_api.py -v`
Expected: FAIL because routes are missing.

- [ ] **Step 2: Implement route modules and include routers**

Routes call services only. Routes do not directly query SQLAlchemy or Redis.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_tasks_api.py backend/tests/test_training_api.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/routes backend/app/main.py backend/tests/test_tasks_api.py backend/tests/test_training_api.py
git commit -m "feat: add task training and websocket routes"
```

---

### Task 9: Independent Worker Executor

**Files:**
- Create: `backend/app/worker/__init__.py`
- Create: `backend/app/worker/executor.py`
- Create: `backend/app/worker/main.py`
- Test: `backend/tests/test_worker_executor.py`

**Interfaces:**
- Produces: `WorkerExecutor.execute(message: QueuedTaskMessage) -> None`.
- Produces: `python -m app.worker.main` loop that consumes queue messages.
- Produces: status/event/log transitions for `queued -> running -> completed|paused|canceled|failed`.

- [ ] **Step 1: Write failing worker tests**

Use fake repositories, fake queue, fake control, fake event stream, and a fake trainer factory. Cover completed, paused, canceled, and failed runs.

Run: `python -m pytest backend/tests/test_worker_executor.py -v`
Expected: FAIL with import errors.

- [ ] **Step 2: Implement worker executor and main loop**

Generate `run_id` per execution. Persist `current_run_id`, episode logs, final status, `total_reward`, and `error_message` when relevant. Publish `status_changed`, `episode_completed`, and `task_failed` events.

- [ ] **Step 3: Run tests**

Run: `python -m pytest backend/tests/test_worker_executor.py -v`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add backend/app/worker backend/tests/test_worker_executor.py
git commit -m "feat: add independent worker executor"
```

---

### Task 10: Alembic Migration Foundation

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/versions/20260701_initial_enterprise_foundation.py`
- Modify: `backend/requirements.txt`
- Modify: `backend/Dockerfile`

**Interfaces:**
- Produces: migration creating `tasks` and `training_logs` with `current_run_id`, `error_message`, `run_id`, and lookup indexes.
- Produces: `alembic upgrade head` using `settings.DATABASE_URL`.

- [ ] **Step 1: Add Alembic dependency**

Add `alembic==1.14.0` to `backend/requirements.txt`.

- [ ] **Step 2: Create migration files**

Migration must explicitly create both tables and indexes. Do not depend on autogenerate in the final committed migration file.

- [ ] **Step 3: Verify migration command**

Run from `backend`: `python -m alembic upgrade head`
Expected: PASS when MySQL is reachable; if MySQL is unavailable locally, document the limitation in the final execution recap.

- [ ] **Step 4: Commit**

```bash
git add backend/alembic.ini backend/migrations backend/requirements.txt backend/Dockerfile
git commit -m "feat: add Alembic migration foundation"
```

---

### Task 11: Docker Compose API/Worker Split

**Files:**
- Modify: `docker-compose.yml`
- Modify: `backend/Dockerfile`

**Interfaces:**
- Produces: `backend-api` service running `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Produces: `backend-worker` service running `python -m app.worker.main`.
- Produces: API healthcheck using `/health/ready`.
- Produces: worker healthcheck using a Python import/connectivity command.

- [ ] **Step 1: Update compose services**

Keep MySQL, Redis, and frontend ports compatible with README: frontend `18080`, backend API `18000`, MySQL `13306`, Redis `16379`.

- [ ] **Step 2: Validate compose config**

Run: `docker-compose config`
Expected: PASS and output contains `backend-api` and `backend-worker`.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml backend/Dockerfile
git commit -m "feat: split API and worker compose services"
```

---

### Task 12: Frontend Compatibility And Encoding Repair

**Files:**
- Modify: `frontend/src/api/index.js`
- Modify: `frontend/src/stores/training.js`
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/views/TaskList.vue`
- Modify: `frontend/src/views/Training.vue`
- Modify: `frontend/src/views/Logs.vue`
- Modify: `frontend/src/components/TaskForm.vue`
- Modify: `frontend/nginx.conf` if WebSocket proxy requires path adjustment.

**Interfaces:**
- Produces: frontend error helper reading `error.message` from unified API envelope.
- Produces: status support for `created`, `queued`, `running`, `paused`, `completed`, `failed`, `canceled`.
- Produces: WebSocket handling for `status_changed`, `episode_completed`, and `task_failed`; preserve backwards-compatible handling for `reward_update` and `status_change` during rollout.
- Produces: fixed Chinese UI text.

- [ ] **Step 1: Fix Chinese mojibake**

Replace corrupted labels/messages in the listed Vue and store files with readable Chinese. Keep UI layout unchanged.

- [ ] **Step 2: Adapt API and WebSocket handling**

Update status maps, button enable/disable rules, and error message extraction.

- [ ] **Step 3: Verify frontend build**

Run: `npm run build --prefix frontend`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add frontend/src frontend/nginx.conf
git commit -m "feat: adapt frontend to enterprise foundation API"
```

---

### Task 13: Final Verification And Cleanup

**Files:**
- Modify: `README.md` only if startup commands changed enough to make current instructions wrong.
- Inspect: all files changed by Tasks 1-12.

**Interfaces:**
- Produces: verified backend tests, frontend build, compose config, and clear final notes for any unavailable external dependency.

- [ ] **Step 1: Run focused backend tests**

Run: `python -m pytest backend/tests -v`
Expected: PASS.

- [ ] **Step 2: Run frontend build**

Run: `npm run build --prefix frontend`
Expected: PASS.

- [ ] **Step 3: Validate compose config**

Run: `docker-compose config`
Expected: PASS.

- [ ] **Step 4: Run smoke imports**

Run: `python -c "import sys; sys.path.insert(0, 'backend'); from app.main import app; from app.worker.executor import WorkerExecutor; print('ok')"`
Expected: `ok`.

- [ ] **Step 5: Commit final docs or cleanup**

```bash
git add README.md
 git diff --cached --quiet || git commit -m "docs: update enterprise foundation run instructions"
```

## Self-Review Checklist

- Spec coverage: backend app package, independent worker, new state model, Redis protocol, Alembic, unified errors, logging/health, frontend compatibility, and verification are covered by Tasks 1-13.
- Placeholder scan: no task uses unresolved markers or vague implementation language.
- Type consistency: `TaskStatus`, `ControlCommand`, `QueuedTaskMessage`, `TaskService`, `TrainingLogService`, `WorkerExecutor`, and event names match the approved spec.
- Scope control: authentication, roles, multi-tenancy, PPO, PyBullet implementation, Kubernetes, Prometheus, and Grafana remain out of scope.

## Execution Options

Plan execution should use one of these two workflows:

1. **Subagent-Driven (recommended)**: use `superpowers:subagent-driven-development`; dispatch a fresh worker per task and review between tasks.
2. **Inline Execution**: use `superpowers:executing-plans`; execute tasks in this session with checkpoints.
