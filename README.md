# Embodied AI Multi-Task Simulation & Training System

一个支持多任务并行训练的具身智能仿真平台，基于 FastAPI + Redis + MySQL + Vue 3 构建，并通过 WebSocket 提供实时训练可视化。

## 系统组成

- 前端控制台：任务管理、训练监控、日志查看
- 后端 API：任务创建、训练控制、日志查询、WebSocket 推送
- 独立 Worker：从 Redis 队列取任务并执行训练
- 训练内核：Q-learning + Gymnasium
- 数据层：MySQL 保存任务与训练日志，Redis 保存队列、控制命令和实时事件流

## 运行方式

### 方式一：Docker Compose（推荐）

1. 复制环境文件并按需修改：

```bash
cp .env.example .env
```

2. 启动全部服务：

```bash
docker-compose up -d --build
```

3. 查看日志：

```bash
docker-compose logs -f
```

4. 停止服务：

```bash
docker-compose down
```

### 访问地址

- 前端：http://localhost:18081
- 后端：http://localhost:18000
- API 文档：http://localhost:18000/docs
- MySQL：localhost:13306
- Redis：localhost:16379

### 方式二：本地开发

后端 API：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端 Worker（另开一个终端）：

```bash
cd backend
python -m app.worker.main
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 使用流程

1. 打开前端并创建一个训练任务。
2. 在任务列表里点击“启动”。
3. 进入“监控”页面查看 reward 曲线和任务状态。
4. 需要中断时点击“暂停”或“取消”。
5. 在“训练日志”里选择任务查看历史记录。

## 任务状态

- created：已创建，尚未入队
- queued：已入队，等待 Worker 执行
- running：正在训练
- paused：已暂停
- completed：已完成
- failed：执行失败
- canceled：已取消

## 当前实现范围

- 已实现：Q-learning、Gymnasium、任务队列、独立 Worker、实时训练流、训练日志、任务状态控制、健康检查、Alembic 迁移基础
- 预留但未完成：PyBullet 环境、PPO 等更多算法、分布式 Worker、鉴权与权限控制

## 项目结构

- `backend/app/`：FastAPI API、Worker、领域规则、应用服务、基础设施和训练核心
- `backend/migrations/`：Alembic 数据库迁移
- `frontend/`：Vue 3 前端控制台
- `docker-compose.yml`：整套服务编排
- `.env.example`：环境变量模板
- `docs/`：设计与计划文档
