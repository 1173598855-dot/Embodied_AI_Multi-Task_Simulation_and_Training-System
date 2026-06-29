from core.agent.base import BaseAgent
from core.environment.base import BaseEnvironment


class Trainer:
    def __init__(self, agent: BaseAgent, env: BaseEnvironment, task_id: int):
        self.agent = agent
        self.env = env
        self.task_id = task_id

    def run(self, episodes: int = 500, callback=None, control_callback=None):
        for ep in range(episodes):
            if control_callback:
                command = control_callback(self.task_id, stage="episode_start", episode=ep)
                if command in {"pause", "cancel"}:
                    return command

            state = self.env.reset()
            total_reward = 0.0

            while True:
                if control_callback:
                    command = control_callback(self.task_id, stage="step", episode=ep)
                    if command in {"pause", "cancel"}:
                        return command

                action = self.agent.choose_action(state)
                next_state, reward, done, _ = self.env.step(action)
                self.agent.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                if done:
                    break

            if callback:
                callback(self.task_id, ep, total_reward, self.agent.epsilon)

        return None
