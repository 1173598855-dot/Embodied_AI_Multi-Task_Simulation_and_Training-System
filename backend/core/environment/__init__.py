from core.environment.base import BaseEnvironment
from core.environment.gym_env import GymEnvironment
from core.environment.pybullet_env import PyBulletEnvironment


class EnvFactory:
    @staticmethod
    def create(env_type: str, env_name: str = None) -> BaseEnvironment:
        if env_type == "gym":
            return GymEnvironment(env_name or "CartPole-v1")
        elif env_type == "robot":
            return PyBulletEnvironment(env_name)
        raise ValueError(f"Unknown env_type: {env_type}")

