from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    def choose_action(self, state: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str):
        raise NotImplementedError
