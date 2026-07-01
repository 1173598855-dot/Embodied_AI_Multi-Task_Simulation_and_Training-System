from abc import ABC, abstractmethod


class BaseEnvironment(ABC):
    @abstractmethod
    def reset(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def step(self, action: int) -> tuple[int, float, bool, dict]:
        raise NotImplementedError

    @abstractmethod
    def action_space_size(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def state_space_size(self) -> int:
        raise NotImplementedError

    def close(self) -> None:
        return None
