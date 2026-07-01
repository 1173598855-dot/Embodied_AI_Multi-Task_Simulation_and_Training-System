import numpy as np

from app.training.agent.base import BaseAgent


class QLearningAgent(BaseAgent):
    def __init__(
        self,
        state_size: int,
        action_size: int,
        lr: float = 0.1,
        gamma: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
    ):
        self.q_table = np.zeros((state_size, action_size))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def choose_action(self, state: int) -> int:
        state = min(state, self.q_table.shape[0] - 1)
        if np.random.random() < self.epsilon:
            return int(np.random.randint(self.q_table.shape[1]))
        return int(np.argmax(self.q_table[state]))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        state = min(state, self.q_table.shape[0] - 1)
        next_state = min(next_state, self.q_table.shape[0] - 1)
        target = reward + (0 if done else self.gamma * np.max(self.q_table[next_state]))
        self.q_table[state][action] += self.lr * (target - self.q_table[state][action])
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, path: str):
        np.save(path, self.q_table)

    def load(self, path: str):
        self.q_table = np.load(path)
