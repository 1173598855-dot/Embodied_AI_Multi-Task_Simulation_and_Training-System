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
        self._thread: threading.Thread | None = None

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
                logger.warning(f"Task {task_id} not found")
                return

            task.status = "running"
            db.commit()
            self.queue.update_status(task_id, {"status": "running"})

            env = EnvFactory.create(task.env_type, task.env_name)
            agent = QLearningAgent(
                state_size=env.state_space_size(),
                action_size=env.action_space_size(),
            )

            if task.config:
                agent.lr = task.config.get("lr", agent.lr)
                agent.gamma = task.config.get("gamma", agent.gamma)
                agent.epsilon = task.config.get("epsilon", agent.epsilon)

            config = task.config or {}
            episodes = config.get("episodes", 500)
            last_reward = 0.0

            def on_episode_done(tid: int, episode: int, reward: float, epsilon: float):
                nonlocal last_reward
                last_reward = reward
                log_entry = TrainingLog(
                    task_id=tid,
                    episode=episode,
                    step=episode,
                    reward=reward,
                )
                db.add(log_entry)
                db.commit()
                self.queue.push_reward_stream(tid, episode, reward, epsilon)

            trainer = Trainer(agent, env, task_id)
            trainer.run(episodes=episodes, callback=on_episode_done)

            task.status = "completed"
            task.total_reward = last_reward
            db.commit()
            self.queue.update_status(task_id, {"status": "completed"})
            logger.info(f"Task {task_id} completed with reward {last_reward:.2f}")

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
