import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest

from app.training.agent.q_learning import QLearningAgent
from app.training.environment import EnvFactory
from app.training.environment.pybullet_env import PyBulletEnvironment


def test_q_learning_agent_initializes_q_table_and_decays_epsilon_on_done():
    agent = QLearningAgent(state_size=4, action_size=2, epsilon=1.0, epsilon_decay=0.5, epsilon_min=0.1)
    assert agent.q_table.shape == (4, 2)

    agent.update(state=0, action=1, reward=1.0, next_state=1, done=True)

    assert agent.epsilon == 0.5
    assert agent.q_table[0][1] > 0


def test_q_learning_agent_clamps_state_to_q_table_bounds():
    agent = QLearningAgent(state_size=2, action_size=2, epsilon=0.0)
    agent.q_table[1] = np.array([1.0, 2.0])

    assert agent.choose_action(99) == 1


def test_env_factory_creates_gym_environment():
    env = EnvFactory.create("gym", "CartPole-v1")
    try:
        assert env.action_space_size() > 0
        assert env.state_space_size() > 0
    finally:
        env.close()


def test_pybullet_environment_is_skeleton_only():
    with pytest.raises(NotImplementedError):
        PyBulletEnvironment("robot-arm")
