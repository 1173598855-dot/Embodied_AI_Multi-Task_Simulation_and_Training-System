from abc import ABC, abstractmethod


class BaseEnvironment(ABC):
    @abstractmethod
    def reset(self) -> int:
        ...

    @abstractmethod
    def step(self, action: int) -> tuple[int, float, bool, dict]:
        ...

    @abstractmethod
    def action_space_size(self) -> int:
        ...

    @abstractmethod
    def state_space_size(self) -> int:
        ...
