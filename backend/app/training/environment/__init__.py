from app.training.environment.base import BaseEnvironment
from app.training.environment.gym_env import GymEnvironment
from app.training.environment.pybullet_env import PyBulletEnvironment


class EnvFactory:
    @staticmethod
    def create(env_type: str, env_name: str | None = None) -> BaseEnvironment:
        if env_type == "gym":
            return GymEnvironment(env_name or "CartPole-v1")
        if env_type == "robot":
            return PyBulletEnvironment(env_name)
        raise ValueError(f"Unknown env_type: {env_type}")
