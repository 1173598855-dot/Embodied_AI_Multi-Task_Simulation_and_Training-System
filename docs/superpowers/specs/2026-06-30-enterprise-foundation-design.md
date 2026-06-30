# Enterprise Foundation Design

> Date: 2026-06-30
> Scope: Phase 1 enterprise foundation refactor for the embodied AI training platform

## 1. Goal

Upgrade the current prototype into a maintainable enterprise-grade foundation while preserving the existing product behavior:

- Task CRUD
- Training start, pause, cancel
- Q-learning training in Gymnasium environments
- Training logs persisted in MySQL
- Real-time training events over WebSocket
- Docker Compose based local deployment

This phase focuses on engineering foundation, not product expansion. Authentication, authorization, multi-tenancy, PPO, PyBullet implementation, Kubernetes, and advanced observability are intentionally out of scope.

## 2. Chosen Approach

Use a modular monolith backend with an independent worker process.

The API service and worker service run as separate processes and Docker Compose services, but share the same backend codebase, database models, domain rules, queue protocol, and training core. This keeps operational boundaries clear without prematurely splitting the project into many microservices.

Rejected alternatives:

- Quasi-microservices: too much deployment and coordination overhead for the current project size.
- Conservative enhancement in-place: lower risk, but does not establish the boundaries needed for future enterprise features.

## 3. Backend Structure

Target backend layout:

```text
backend/
  app/
    api/
      routes/
      schemas/
      deps.py
    core/
      config.py
      errors.py
      logging.py
      lifecycle.py
    domain/
      task_state.py
      task_rules.py
      training_config.py
    application/
      task_service.py
      training_log_service.py
    infrastructure/
      db/
      repositories/
      redis/
      migrations/
    training/
      agent/
      environment/
      trainer.py
    worker/
      main.py
      executor.py
    main.py
  alembic/
  tests/
```

Responsibilities:

- `api/`: HTTP and WebSocket adapters only. Routes validate requests, call application services, and return response models. Routes do not directly use SQLAlchemy, Redis, or training internals.
- `core/`: cross-cutting runtime concerns such as settings, logging, error handling, request IDs, and application startup.
- `domain/`: pure business rules such as task states, allowed transitions, control commands, and training configuration validation. This layer avoids database and Redis dependencies.
- `application/`: use-case services such as task creation, training start, pause, cancel, and log retrieval. API and worker code call these services.
- `infrastructure/`: SQLAlchemy models, repositories, session management, Redis queue, Redis event stream, and Alembic migration integration.
- `training/`: Q-learning agent, environment adapters, and trainer loop. PPO and PyBullet implementation remain out of scope.
- `worker/`: independent worker entrypoint and task execution orchestration.

## 4. Runtime Architecture

Docker Compose should run at least these services:

- `mysql`: MySQL 8.0 persistence.
- `redis`: Redis queue, control commands, and real-time event streams.
- `backend-api`: FastAPI process serving REST API, WebSocket, and health checks.
- `backend-worker`: worker process consuming Redis tasks and running training.
- `frontend`: Vue app served by nginx.

The API process must not start the worker in FastAPI lifespan. Worker startup becomes explicit, for example:

```bash
python -m app.worker.main
```

The API entrypoint remains explicit, for example:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 5. Task State Model

Current prototype states are refined into a clearer enterprise state model:

```text
created -> queued -> running -> completed
                 \-> paused
                 \-> canceled
                 \-> failed
```

State meanings:

- `created`: task exists but has not been queued for execution.
- `queued`: task has been submitted to Redis and is waiting for a worker.
- `running`: worker is executing the training loop.
- `paused`: worker stopped at a control boundary and task may be started again.
- `completed`: task finished successfully.
- `failed`: task ended due to an error and may be started again.
- `canceled`: task was explicitly canceled and cannot be restarted in phase 1.

Start rules for phase 1:

- Allowed: `created`, `paused`, `failed`.
- Rejected: `queued`, `running`, `completed`, `canceled`.

Delete rules for phase 1:

- Allowed: `created`, `completed`, `failed`, `canceled`.
- Rejected: `queued`, `running`, `paused`.

Cancel rules for phase 1:

- Allowed: `created`, `queued`, `running`, `paused`, `failed`.
- Rejected: `completed`, `canceled`.

Pause rules for phase 1:

- Allowed: `queued`, `running`.
- Rejected: all other states.

## 6. Queue And Event Protocol

Training start writes a structured Redis queue message rather than a bare task ID:

```json
{
  "task_id": 12,
  "requested_at": "2026-06-30T15:00:00+08:00",
  "attempt": 1
}
```

The worker consumes messages, validates the referenced task, marks it running, executes training, and updates final state.

Control commands remain simple Redis keys in phase 1:

```text
task:{id}:control -> pause | cancel
```

Real-time events use one Redis Stream per task:

```text
task:{id}:events
```

Event types:

- `status_changed`
- `episode_completed`
- `task_failed`

Example `episode_completed` payload:

```json
{
  "type": "episode_completed",
  "task_id": 12,
  "run_id": "...",
  "episode": 42,
  "reward": 18.0,
  "avg_reward": 16.4,
  "epsilon": 0.81
}
```

MySQL is the durable source for tasks and historical logs. Redis is used for queueing, control commands, and short-lived real-time event delivery.

## 7. Database And Migrations

Move from `Base.metadata.create_all()` as the main schema strategy to Alembic migrations.

Initial migration should create or normalize:

- `tasks`
- `training_logs`
- indexes for task status and task log lookup
- state values aligned with the new model
- `tasks.current_run_id` for the active or most recent worker run
- `tasks.error_message` for the latest failure reason
- `training_logs.run_id` so logs can be tied to a specific worker execution

The application can keep a development convenience path if necessary, but production-style startup should rely on migrations.

## 8. Error Handling

Define application error classes:

- `AppError`
- `NotFoundError`
- `ConflictError`
- `ValidationAppError`
- `InfrastructureError`

All API errors should use a stable response shape:

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task not found",
    "details": {}
  }
}
```

Routes should raise application errors or let services raise them. FastAPI exception handlers translate them into HTTP responses.

Frontend error handling should read this shape and fall back gracefully for unexpected errors.

## 9. Logging And Health Checks

Use structured logs for API and worker. Important fields include:

- `request_id`
- `run_id`
- `task_id`
- `event`
- `status`
- `duration_ms`
- `error`

API requests generate or propagate `X-Request-ID`. Worker task execution generates a `run_id` that appears in task status events, logs, and failures.

Health endpoints:

- `GET /health/live`: returns success if the API process is alive.
- `GET /health/ready`: checks MySQL and Redis connectivity.

Worker health should be implemented through a lightweight container health command that imports the worker code and checks DB/Redis connectivity.

## 10. Frontend Scope

Frontend changes are limited to compatibility and basic polish:

- Fix existing Chinese mojibake in Vue files and store messages.
- Keep routes and main workflows unchanged.
- Adapt task states to `created` and `queued`.
- Adapt WebSocket event names to `status_changed`, `episode_completed`, and `task_failed`.
- Adapt error handling to the unified API error format.
- Keep `npm run build` passing.

No major UI redesign is included in phase 1.

## 11. Testing Strategy

Add tests at three levels:

1. Unit tests:
   - task state transitions
   - training configuration validation
   - Q-learning basic behavior
   - trainer pause/cancel control behavior

2. Application service tests:
   - create task
   - start task
   - pause task
   - cancel task
   - delete task rules
   - list training logs

   These should use fake repositories and queues where practical.

3. API tests:
   - root route
   - health routes
   - task core routes
   - training control routes
   - unified error response format

Verification commands for phase 1 completion:

```bash
python -m pytest backend/tests
npm run build --prefix frontend
docker-compose build
```

If Docker is unavailable in the local environment, document that limitation and still verify Python and frontend builds.

## 12. Delivery Boundaries

Included in phase 1:

- Backend `app/` package refactor
- API and worker split into separate processes
- Docker Compose worker service
- Alembic migration foundation
- Unified settings, logging, and errors
- Health checks
- Existing training workflow migrated to the new architecture
- Redis queue and event protocol cleanup
- Frontend compatibility and mojibake fix
- Focused tests

Excluded from phase 1:

- Login, JWT, roles, permissions
- Multi-tenant organizations
- Audit trail beyond basic logs and task status
- PPO implementation
- Full PyBullet implementation
- Advanced concurrent scheduling policy
- Kubernetes or Helm
- Prometheus and Grafana
- Full end-to-end Docker integration test suite

## 13. Acceptance Criteria

The phase is complete when:

- The API starts without launching an embedded worker.
- The worker starts independently and can process queued training tasks.
- Docker Compose defines separate API and worker services.
- Existing task management, training control, logs, and WebSocket monitoring still work.
- Task states use the new `created` and `queued` model consistently.
- API errors follow the unified error format.
- Health checks exist and report DB/Redis readiness.
- Alembic migration files exist for the schema.
- Frontend Chinese text renders correctly.
- Backend tests pass in an environment with dependencies installed.
- Frontend production build passes.
