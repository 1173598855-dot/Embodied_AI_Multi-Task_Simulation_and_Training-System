from app.training.agent.base import BaseAgent
from app.training.environment.base import BaseEnvironment


class Trainer:
    def __init__(self, agent: BaseAgent, env: BaseEnvironment, task_id: int, run_id: str):
        self.agent = agent
        self.env = env
        self.task_id = task_id
        self.run_id = run_id

    def run(self, episodes: int = 500, on_episode=None, on_control=None):
        for episode in range(episodes):
            if on_control:
                command = on_control(self.task_id, episode, "episode_start")
                if command in {"pause", "cancel"}:
                    return command

            state = self.env.reset()
            total_reward = 0.0

            while True:
                if on_control:
                    command = on_control(self.task_id, episode, "step")
                    if command in {"pause", "cancel"}:
                        return command

                action = self.agent.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                self.agent.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                if done:
                    break

            if on_episode:
                on_episode(self.task_id, self.run_id, episode, total_reward, self.agent.epsilon)

        return None
