from core.environment.base import BaseEnvironment


class PyBulletEnvironment(BaseEnvironment):
    def __init__(self, urdf_path: str = None):
        raise NotImplementedError("PyBullet environment is not yet implemented")

    def reset(self) -> int:
        raise NotImplementedError

    def step(self, action: int) -> tuple[int, float, bool, dict]:
        raise NotImplementedError

    def action_space_size(self) -> int:
        raise NotImplementedError

    def state_space_size(self) -> int:
        raise NotImplementedError

