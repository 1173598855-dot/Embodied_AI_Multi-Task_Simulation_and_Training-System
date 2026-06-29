import logging
import threading
import time

from core.agent.q_learning import QLearningAgent
from core.environment import EnvFactory
from core.trainer import Trainer
from db.database import SessionLocal
from db.models import Task, TrainingLog
from worker.redis_queue import TaskQueue

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

    def stop(self):
        self.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

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
                logger.warning("Task %s not found", task_id)
                return

            task.status = "running"
            db.commit()
            self.queue.update_status(task_id, {"status": "running"})
            self.queue.clear_control_command(task_id)

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
            reward_window: list[float] = []

            def get_control_command(_: int, stage: str, episode: int):
                command = self.queue.get_control_command(task_id)
                if command == "pause":
                    task.status = "paused"
                    db.commit()
                    self.queue.update_status(task_id, {"status": "paused", "stage": stage, "episode": episode})
                    return "pause"
                if command == "cancel":
                    task.status = "canceled"
                    db.commit()
                    self.queue.update_status(task_id, {"status": "canceled", "stage": stage, "episode": episode})
                    return "cancel"
                return None

            def on_episode_done(tid: int, episode: int, reward: float, epsilon: float):
                nonlocal last_reward
                last_reward = reward
                reward_window.append(reward)
                if len(reward_window) > 20:
                    reward_window.pop(0)
                avg_reward = sum(reward_window) / len(reward_window)
                log_entry = TrainingLog(
                    task_id=tid,
                    episode=episode,
                    step=episode + 1,
                    reward=reward,
                    avg_reward=avg_reward,
                )
                db.add(log_entry)
                db.commit()
                self.queue.push_reward_stream(tid, episode, reward, epsilon)

            trainer = Trainer(agent, env, task_id)
            result = trainer.run(episodes=episodes, callback=on_episode_done, control_callback=get_control_command)

            if result == "pause":
                logger.info("Task %s paused", task_id)
                return
            if result == "cancel":
                logger.info("Task %s canceled", task_id)
                return

            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "completed"
                task.total_reward = last_reward
                db.commit()
            self.queue.update_status(task_id, {"status": "completed", "total_reward": last_reward})
            logger.info("Task %s completed with reward %.2f", task_id, last_reward)

        except Exception as exc:
            logger.error("Task %s failed: %s", task_id, exc)
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = "failed"
                    db.commit()
                self.queue.update_status(task_id, {"status": "failed", "error": str(exc)})
            except Exception:
                pass
        finally:
            db.close()
