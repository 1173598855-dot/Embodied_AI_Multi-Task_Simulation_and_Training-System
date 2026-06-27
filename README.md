# 🤖 具身智能多任务仿真训练平台

> Embodied AI Multi-Task Simulation & Training System

一个支持多任务并行训练的具身智能仿真平台，基于 **FastAPI + Redis + Vue 3** 构建，通过 WebSocket 实现实时训练可视化。

---

## 📸 系统架构

```
┌─────────────────────────────────────┐
│        前端控制台 UI (Vue 3)         │
│  仪表盘 / 任务管理 / 训练曲线 / 日志  │
└──────────────┬──────────────────────┘
               ↓ WebSocket + REST API
┌─────────────────────────────────────┐
│      AI 任务调度中心 (FastAPI)        │
│     Redis Queue + Worker 线程        │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│    具身智能执行层 (Q-learning Agent)  │
│       Gym / PyBullet 环境            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│      数据层 (MySQL + Redis)          │
│    任务管理 / 训练日志 / 实时流        │
└─────────────────────────────────────┘
```

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| **多任务并行训练** | Redis Queue 调度，支持多任务同时运行 |
| **多环境切换** | Gymnasium（CartPole 等）+ PyBullet 预留接口 |
| **实时训练可视化** | WebSocket 推送 + ECharts reward 曲线 |
| **可扩展 Agent** | BaseAgent 抽象类，Q-learning → PPO 无缝扩展 |
| **Docker 一键部署** | 4 容器编排，`docker-compose up` 即可运行 |

## 🛠️ 技术栈

**后端：**
- Python 3.11 + FastAPI
- SQLAlchemy + MySQL 8.0
- Redis 7（任务队列 + 实时数据流）
- Gymnasium（OpenAI Gym 继任者）
- NumPy（Q-learning 计算）

**前端：**
- Vue 3 + Vite
- Element Plus（UI 组件库）
- ECharts（训练曲线可视化）
- Pinia（状态管理）
- Axios（HTTP 客户端）

**部署：**
- Docker Compose（4 容器编排）
- Nginx（静态文件 + 反向代理）

## 🚀 快速开始

### 环境要求

- Docker Desktop（已安装并运行）
- Git

### 一键启动

```bash
# 克隆项目
git clone git@github.com:1173598855-dot/Embodied_AI_Multi-Task_Simulation_and_Training-System.git
cd Embodied_AI_Multi-Task_Simulation_and_Training-System

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 🖥️ 前端控制台 | http://localhost:18080 |
| 🔌 后端 API | http://localhost:18000 |
| 📊 API 文档 | http://localhost:18000/docs |
| 🗄️ MySQL | localhost:13306 |
| 📦 Redis | localhost:16379 |

### 停止服务

```bash
docker-compose down
```

## 📖 使用指南

### 1. 创建训练任务

打开前端控制台 → 任务管理 → 新建任务

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 任务名称 | 自定义任务名 | - |
| 环境类型 | Gym / PyBullet | gym |
| 环境名称 | Gym 环境名 | CartPole-v1 |
| 训练轮数 | Episode 数量 | 500 |
| 学习率 | Q-learning 学习率 | 0.1 |
| 折扣因子 | 折扣因子 γ | 0.99 |

### 2. 启动训练

在任务列表中点击「启动」按钮，任务将进入 Redis 队列等待执行。

### 3. 实时监控

点击「监控」按钮进入训练监控页面：
- **Reward 曲线**：散点图 + 20 轮滑动平均
- **Epsilon 衰减**：探索率变化曲线
- **任务状态**：实时显示 pending / running / completed / failed

## 📁 项目结构

```
.
├── docker-compose.yml          # Docker 编排配置
├── .env.example                # 环境变量模板
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 应用入口
│   ├── config.py               # 配置管理
│   ├── api/routes/             # REST API 路由
│   │   ├── tasks.py            # 任务 CRUD
│   │   ├── training.py         # 训练控制
│   │   └── ws.py               # WebSocket 实时推送
│   ├── core/                   # 核心业务逻辑
│   │   ├── agent/              # AI Agent 实现
│   │   │   ├── base.py         # BaseAgent 抽象类
│   │   │   └── q_learning.py   # Q-learning 算法
│   │   ├── environment/        # 仿真环境
│   │   │   ├── base.py         # BaseEnvironment 抽象类
│   │   │   ├── gym_env.py      # Gymnasium 适配器
│   │   │   └── pybullet_env.py # PyBullet 骨架
│   │   └── trainer.py          # 训练循环
│   ├── worker/                 # 任务执行器
│   │   ├── redis_queue.py      # Redis 队列封装
│   │   └── task_worker.py      # 后台 Worker
│   └── db/                     # 数据库层
│       ├── models.py           # SQLAlchemy 模型
│       └── schemas.py          # Pydantic 数据模型
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── stores/             # Pinia 状态管理
│   │   └── api/                # Axios 封装
│   └── nginx.conf              # Nginx 配置
└── docs/                       # 项目文档
```

## 🔧 开发指南

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

### 添加新 Agent

1. 在 `backend/core/agent/` 下创建新文件
2. 继承 `BaseAgent` 抽象类
3. 实现 `choose_action` 和 `update` 方法
4. 在 Worker 中注册新算法

```python
from core.agent.base import BaseAgent

class PPOAgent(BaseAgent):
    def choose_action(self, state: int) -> int:
        # PPO 策略网络推理
        pass

    def update(self, state, action, reward, next_state, done):
        # PPO 更新逻辑
        pass
```

### 添加新环境

1. 在 `backend/core/environment/` 下创建新文件
2. 继承 `BaseEnvironment` 抽象类
3. 在 `EnvFactory` 中注册

```python
from core.environment.base import BaseEnvironment

class PyBulletEnvironment(BaseEnvironment):
    def __init__(self, urdf_path: str):
        import pybullet as p
        self.physics_client = p.connect(p.GUI)
        self.robot = p.loadURDF(urdf_path)

    def reset(self) -> int:
        # 重置环境
        pass

    def step(self, action: int) -> tuple[int, float, bool, dict]:
        # 执行动作
        pass
```

## 📊 API 文档

启动后访问 http://localhost:18000/docs 查看完整的 Swagger API 文档。

### 主要接口

| Method | Endpoint | 说明 |
|--------|----------|------|
| GET | `/api/tasks` | 获取任务列表 |
| POST | `/api/tasks` | 创建新任务 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| POST | `/api/training/{id}/start` | 启动训练 |
| POST | `/api/training/{id}/pause` | 暂停训练 |
| GET | `/api/training/{id}/logs` | 获取训练日志 |
| WS | `/ws/{task_id}` | WebSocket 实时数据流 |

## 🗄️ 数据库设计

### tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| name | VARCHAR(128) | 任务名称 |
| env_type | VARCHAR(32) | 环境类型 (gym/robot) |
| env_name | VARCHAR(64) | 环境名称 |
| algo | VARCHAR(32) | 算法类型 |
| status | VARCHAR(16) | 状态 (pending/running/completed/failed) |
| config | JSON | 超参数配置 |
| total_reward | FLOAT | 总奖励值 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### training_logs 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| task_id | INT | 关联任务 ID |
| episode | INT | 轮次 |
| step | INT | 步数 |
| reward | FLOAT | 奖励值 |
| avg_reward | FLOAT | 平均奖励 |
| created_at | DATETIME | 创建时间 |

## 🔮 未来规划

- [ ] PPO 强化学习算法集成
- [ ] PyBullet 机器人仿真环境完整实现
- [ ] 分布式 Worker 水平扩展
- [ ] 训练模型导出与加载
- [ ] 数据爬虫模块（RL 算法资料采集）
- [ ] 用户认证与权限管理
- [ ] 训练任务定时调度
- [ ] 多 GPU 支持

## 📝 更新日志

### v1.0.0 (2026-06-27)

**🎉 首次发布**

**核心功能：**
- ✅ Q-learning 强化学习算法实现
- ✅ Gymnasium 仿真环境集成（CartPole-v1）
- ✅ Redis 任务队列系统
- ✅ FastAPI REST API
- ✅ WebSocket 实时训练数据推送
- ✅ Vue 3 前端控制台
- ✅ ECharts 训练曲线可视化
- ✅ Docker Compose 一键部署

**技术特性：**
- BaseAgent 抽象类，支持算法扩展
- BaseEnvironment 抽象类，支持环境扩展
- PyBullet 环境骨架接口预留
- 训练日志持久化存储
- 实时 reward 曲线与 epsilon 衰减可视化

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**1173598855-dot**

- GitHub: [@1173598855-dot](https://github.com/1173598855-dot)

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [ECharts](https://echarts.apache.org/) - 可视化图表库
- [Gymnasium](https://gymnasium.farama.org/) - 强化学习环境
- [Redis](https://redis.io/) - 内存数据库
- [Docker](https://www.docker.com/) - 容器化平台

---

**⭐ 如果这个项目对你有帮助，请给个 Star 支持一下！**