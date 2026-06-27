from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    def choose_action(self, state: int) -> int:
        ...

    @abstractmethod
    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        ...

    @abstractmethod
    def save(self, path: str):
        ...

    @abstractmethod
    def load(self, path: str):
        ...
