# Embodied AI Multi-Task Simulation & Training System — Design Spec

> 日期: 2026-06-27
> 定位: 可扩展原型平台（模块化，后续可接更多 RL 算法和仿真环境）

---

## 1. 项目概述

一个支持多任务并行训练的具身智能仿真平台。用户通过 Web 控制台创建训练任务，系统通过 Redis 队列调度 Worker，执行 Q-learning Agent 在 Gym 仿真环境中的训练，并通过 WebSocket 实时推送训练曲线到前端。

### 核心能力
- 多任务并行训练（Redis Queue 调度）
- 多环境切换（Gym / PyBullet 接口预留）
- 实时训练可视化（WebSocket + ECharts）
- 可扩展 AI Agent 系统（Q-learning → PPO 预留）
- Docker Compose 一键部署

---

## 2. 技术选型

| 维度 | 选型 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts + Pinia |
| 后端 | FastAPI + SQLAlchemy + Pydantic |
| 任务队列 | Redis List（LPUSH/RPOP） |
| 数据库 | MySQL 8.0 |
| 缓存/消息 | Redis 7 |
| RL 框架 | 手写 Q-learning + Gymnasium |
| 仿真环境 | Gymnasium（CartPole-v1 等），PyBullet 留接口 |
| 部署 | Docker Compose（4 容器） |

---

## 3. 系统架构

### 3.1 服务拓扑

`
┌─────────────┐     ┌──────────────┐     ┌─────────┐     ┌─────────┐
│  Vue 前端    │────▶│  FastAPI 后端  │────▶│  Redis  │     │  MySQL  │
│  (nginx)    │     │  (含 Worker)  │────▶│         │────▶│         │
└─────────────┘     └──────────────┘     └─────────┘     └─────────┘
     :80              :8000              :6379          :3306
`

- 前端由 nginx 提供静态文件服务 + 反向代理 API/WebSocket 请求
- FastAPI 启动时拉起一个后台线程运行 Worker（消费 Redis Queue）
- MySQL 存持久数据（任务、训练日志），Redis 存队列 + 实时状态（reward 流）

### 3.2 数据流

`
用户创建任务 → MySQL(tasks: pending) + Redis LPUSH task_queue
Worker 取任务 → Redis RPOP → 更新 MySQL(status: running)
训练中 → 每 episode 写 MySQL(training_logs) + Redis Stream
WebSocket → 读 Redis Stream → 推送前端 ECharts
任务完成 → MySQL(status: completed, total_reward)
`

---

## 4. 项目结构

`
Embodied_AI_Multi-Task_Simulation_and_Training System/
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # FastAPI 入口，启动 Worker 线程
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py           # CRUD 任务接口
│   │   │   ├── training.py        # 训练控制（启动/暂停/停止）
│   │   │   └── ws.py              # WebSocket 推送训练状态
│   │   └── deps.py                # 依赖注入（DB session, Redis）
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseAgent 抽象类
│   │   │   └── q_learning.py      # Q-learning 实现
│   │   ├── environment/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseEnvironment 抽象类
│   │   │   ├── gym_env.py         # Gym 环境适配器
│   │   │   └── pybullet_env.py    # PyBullet 环境（骨架/接口）
│   │   └── trainer.py             # 训练循环：env.reset -> agent.step -> update
│   │
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── task_worker.py         # 消费 Redis 队列，调度 trainer
│   │   └── redis_queue.py         # Redis 队列操作封装
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy 模型
│   │   ├── schemas.py             # Pydantic 请求/响应模型
│   │   └── database.py            # 数据库连接配置
│   │
│   └── config.py                  # 全局配置（环境变量读取）
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router/
│       │   └── index.js
│       ├── views/
│       │   ├── Dashboard.vue      # 总览仪表盘
│       │   ├── TaskList.vue       # 任务管理
│       │   ├── Training.vue       # 训练监控（ECharts 曲线）
│       │   └── Logs.vue           # 日志查看
│       ├── components/
│       │   ├── RewardChart.vue    # ECharts reward 曲线
│       │   ├── StepChart.vue      # ECharts step 曲线
│       │   └── TaskForm.vue       # 创建任务表单
│       ├── api/
│       │   └── index.js           # Axios 封装
│       └── stores/
│           └── training.js        # Pinia：WebSocket 连接 + 训练状态
│
└── docs/
    └── superpowers/
        └── specs/
`

---

## 5. 数据层设计

### 5.1 MySQL 表结构

`sql
-- 任务表
CREATE TABLE tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    env_type    VARCHAR(32) NOT NULL DEFAULT 'gym',
    env_name    VARCHAR(64) NOT NULL DEFAULT 'CartPole-v1',
    algo        VARCHAR(32) NOT NULL DEFAULT 'q_learning',
    status      VARCHAR(16) NOT NULL DEFAULT 'pending',
    config      JSON,
    total_reward FLOAT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 训练日志表
CREATE TABLE training_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    task_id     INT NOT NULL,
    episode     INT NOT NULL,
    step        INT NOT NULL,
    reward      FLOAT NOT NULL,
    avg_reward  FLOAT,
    state_snapshot TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    INDEX idx_task_episode (task_id, episode)
);
`

### 5.2 Redis 数据结构

| Key | 类型 | 用途 | TTL |
|-----|------|------|-----|
| 	ask_queue | List | 任务队列，LPUSH/RPOP | 无 |
| 	ask:{id}:status | String | 当前训练状态快照 | 30min |
| 	ask:{id}:reward_stream | Stream | reward 实时数据流 | 1h |
| 	ask:{id}:config | Hash | 训练超参数缓存 | 30min |

---

## 6. 核心层设计

### 6.1 环境抽象层

`python
# core/environment/base.py
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
`

- GymEnvironment: 适配 Gymnasium（CartPole-v1 等），连续 state 通过 hash 离散化到 512 桶
- PyBulletEnvironment: 骨架接口，NotImplementedError，后续实现

`python
class EnvFactory:
    @staticmethod
    def create(env_type: str, env_name: str = None) -> BaseEnvironment:
        if env_type == "gym":
            return GymEnvironment(env_name or "CartPole-v1")
        elif env_type == "robot":
            return PyBulletEnvironment(env_name)
        raise ValueError(f"Unknown env_type: {env_type}")
`

### 6.2 Agent 抽象层

`python
# core/agent/base.py
class BaseAgent(ABC):
    @abstractmethod
    def choose_action(self, state: int) -> int: ...

    @abstractmethod
    def update(self, state, action, reward, next_state, done): ...

    @abstractmethod
    def save(self, path: str): ...

    @abstractmethod
    def load(self, path: str): ...
`

- QLearningAgent: epsilon-greedy Q-learning
  - 参数: lr=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01
  - Q-table: numpy 2D array
  - 扩展预留: PPO 在 core/agent/ 下新建文件继承 BaseAgent

### 6.3 训练循环

`python
class Trainer:
    def __init__(self, agent, env, task_id): ...
    def run(self, episodes=500, callback=None):
        for ep in range(episodes):
            state = env.reset()
            total_reward = 0
            while True:
                action = agent.choose_action(state)
                next_state, reward, done, _ = env.step(action)
                agent.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                if done:
                    break
            callback(task_id, ep, total_reward, agent.epsilon)
`

---

## 7. 任务队列系统

### 7.1 Redis Queue 封装

`python
class TaskQueue:
    def __init__(self, redis_url="redis://redis:6379"): ...
    def push(self, task_id): self.redis.lpush("task_queue", task_id)
    def pop(self) -> int | None: ...
    def size(self) -> int: ...
    def update_status(self, task_id, data): ...
    def push_reward_stream(self, task_id, episode, reward, epsilon): ...
`

### 7.2 Worker

- TaskWorker: 守护线程，0.5s 轮询 Redis 队列
- 取到 task_id → 查 MySQL → 初始化 Env + Agent → 调用 Trainer.run()
- 每 episode 回调: 写 training_logs + 推 Redis Stream
- 异常处理: 更新 task.status = "failed"

### 7.3 启动流程

main.py 启动时:
1. 初始化 FastAPI app
2. 注册路由 (tasks, training, ws)
3. 创建 TaskQueue 实例
4. 创建 TaskWorker 并调用 start() 启动后台线程

---

## 8. API 接口设计

### 8.1 REST API

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/tasks | 任务列表 |
| POST | /api/tasks | 创建任务 |
| GET | /api/tasks/{id} | 任务详情 |
| DELETE | /api/tasks/{id} | 删除任务 |
| POST | /api/training/{id}/start | 启动训练（入队） |
| POST | /api/training/{id}/pause | 暂停训练 |
| GET | /api/training/{id}/logs | 查询训练日志 |
| WS | /ws/{task_id} | WebSocket 实时 reward 流 |

### 8.2 创建任务请求体

`json
{
  "name": "CartPole Q-learning 训练",
  "env_type": "gym",
  "env_name": "CartPole-v1",
  "algo": "q_learning",
  "config": {
    "episodes": 500,
    "lr": 0.1,
    "gamma": 0.99,
    "epsilon": 1.0
  }
}
`

### 8.3 WebSocket 协议

`json
{
  "type": "reward_update",
  "episode": 42,
  "reward": 12.5,
  "epsilon": 0.81,
  "timestamp": "2026-06-27T15:00:00"
}

{
  "type": "status_change",
  "status": "completed",
  "total_reward": 450.2
}
`

---

## 9. 前端设计

### 9.1 页面路由

| 页面 | 路由 | 功能 |
|------|------|------|
| 仪表盘 | / | 任务总数、运行中数量、成功率统计卡片 |
| 任务管理 | /tasks | 任务列表表格 + 创建任务弹窗 + 启动/删除操作 |
| 训练监控 | /training/:id | ECharts 实时 reward 曲线 + step 曲线 + epsilon 衰减曲线 |
| 训练日志 | /logs | 按任务筛选的日志表格 |

### 9.2 WebSocket 前端流程

`
进入训练监控页 → 连接 ws://host/ws/{task_id}
收到 reward_update → 更新 Pinia store → ECharts 追加数据点
收到 status_change → 更新任务状态标签
离开页面 → 断开 WebSocket
`

### 9.3 ECharts 曲线组件

- X 轴: episode
- Y 轴: reward / avg_reward（左），epsilon（右）
- 实时追加数据点，保留最近 2000 个点渲染
- 双 Y 轴设计

---

## 10. Docker Compose 部署

`yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: 
      MYSQL_DATABASE: embodied_ai
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: mysql+aiomysql://root:@mysql:3306/embodied_ai
      REDIS_URL: redis://redis:6379

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
`

### 启动方式

`ash
docker-compose up -d
docker-compose logs -f backend
docker-compose down
`

---

## 11. 设计决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 架构风格 | 精简分层（方案 A） | 原型平台够用，后续可平滑迁移微服务 |
| Worker 部署 | 内嵌后台线程 | 降低复杂度，单进程闭环 |
| RL 算法 | 手写 Q-learning | 不引入 Stable-Baselines3 依赖，代码量可控 |
| 状态离散化 | hash % 512 桶 | Gym 部分环境 state 是连续的，简单离散化够用 |
| 实时推送 | Redis Stream + WebSocket | Stream 做缓冲，WebSocket 做推送，解耦 |
| 数据爬虫 | 仅留骨架接口 | 与核心训练系统独立，先跑通主线 |

---

## 12. 扩展预留

- **加新 RL 算法**: core/agent/ 下新建 ppo.py，继承 BaseAgent
- **加新仿真环境**: 实现 PyBulletEnvironment，通过 EnvFactory 分发
- **加爬虫模块**: 新建 crawler/ 目录，实现后写入 MySQL dataset 表
- **加任务调度策略**: 修改 TaskWorker._run()，加优先级/并发控制
- **Worker 水平扩展**: 将 Worker 独立成容器，多实例消费同一队列
