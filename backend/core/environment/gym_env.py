import gymnasium as gym
import numpy as np
from core.environment.base import BaseEnvironment


class GymEnvironment(BaseEnvironment):
    DISCRETE_BINS = 512

    def __init__(self, env_name: str = "CartPole-v1"):
        self.env = gym.make(env_name)
        self.env_name = env_name

    def _discretize(self, state) -> int:
        if isinstance(state, (int, np.integer)):
            return int(state)
        return hash(state.tobytes()) % self.DISCRETE_BINS

    def reset(self) -> int:
        state, _ = self.env.reset()
        return self._discretize(state)

    def step(self, action: int) -> tuple[int, float, bool, dict]:
        state, reward, terminated, truncated, info = self.env.step(action)
        return self._discretize(state), reward, terminated or truncated, info

    def action_space_size(self) -> int:
        return self.env.action_space.n

    def state_space_size(self) -> int:
        if hasattr(self.env.observation_space, "n"):
            return self.env.observation_space.n
        return self.DISCRETE_BINS

