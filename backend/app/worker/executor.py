from app.domain.training_config import parse_training_config
from app.infrastructure.redis.queue import QueuedTaskMessage
from app.training.agent.q_learning import QLearningAgent
from app.training.environment import EnvFactory
from app.training.trainer import Trainer


class WorkerExecutor:
    def __init__(
        self,
        task_repository,
        training_log_repository,
        event_stream,
        task_control,
        trainer_factory=None,
    ):
        self.task_repository = task_repository
        self.training_log_repository = training_log_repository
        self.event_stream = event_stream
        self.task_control = task_control
        self.trainer_factory = trainer_factory or self._build_trainer

    def execute(self, message: QueuedTaskMessage) -> None:
        task = self.task_repository.get(message.task_id)
        if task is None:
            return
        run_id = message.run_id
        self.task_repository.set_run(task.id, run_id)
        self.task_repository.set_status(task.id, "running")
        self.event_stream.publish(task.id, {"type": "status_changed", "task_id": task.id, "run_id": run_id, "status": "running"})
        last_reward = 0.0
        reward_window: list[float] = []

        def on_episode(task_id: int, current_run_id: str, episode: int, reward: float, epsilon: float) -> None:
            nonlocal last_reward
            last_reward = reward
            reward_window.append(reward)
            if len(reward_window) > 20:
                reward_window.pop(0)
            avg_reward = sum(reward_window) / len(reward_window)
            self.training_log_repository.create(
                task_id=task_id,
                run_id=current_run_id,
                episode=episode,
                step=episode + 1,
                reward=reward,
                avg_reward=avg_reward,
            )
            self.event_stream.publish(
                task_id,
                {
                    "type": "episode_completed",
                    "task_id": task_id,
                    "run_id": current_run_id,
                    "episode": episode,
                    "reward": reward,
                    "avg_reward": avg_reward,
                    "epsilon": epsilon,
                },
            )

        def on_control(task_id: int, episode: int, stage: str):
            command = self.task_control.get_command(task_id)
            return command.value if command is not None else None

        try:
            trainer = self.trainer_factory(task, run_id)
            result = trainer.run(episodes=parse_training_config(task.config).episodes, on_episode=on_episode, on_control=on_control)
            if result == "pause":
                self.task_repository.set_status(task.id, "paused")
                self.event_stream.publish(task.id, {"type": "status_changed", "task_id": task.id, "run_id": run_id, "status": "paused"})
                return
            if result == "cancel":
                self.task_repository.set_status(task.id, "canceled")
                self.event_stream.publish(task.id, {"type": "status_changed", "task_id": task.id, "run_id": run_id, "status": "canceled"})
                return
            self.task_repository.set_total_reward(task.id, last_reward)
            self.task_repository.set_status(task.id, "completed")
            self.event_stream.publish(task.id, {"type": "status_changed", "task_id": task.id, "run_id": run_id, "status": "completed"})
        except Exception as exc:
            self.task_repository.set_error(task.id, str(exc))
            self.task_repository.set_status(task.id, "failed")
            self.event_stream.publish(
                task.id,
                {"type": "task_failed", "task_id": task.id, "run_id": run_id, "status": "failed", "error": str(exc)},
            )

    def _build_trainer(self, task, run_id: str) -> Trainer:
        env = EnvFactory.create(task.env_type, task.env_name)
        config = parse_training_config(task.config)
        agent = QLearningAgent(
            state_size=env.state_space_size(),
            action_size=env.action_space_size(),
            lr=config.lr,
            gamma=config.gamma,
            epsilon=config.epsilon,
            epsilon_decay=config.epsilon_decay,
            epsilon_min=config.epsilon_min,
        )
        return Trainer(agent, env, task.id, run_id)
