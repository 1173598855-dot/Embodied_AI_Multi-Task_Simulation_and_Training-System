import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.training.trainer import Trainer


class FakeAgent:
    epsilon = 0.7

    def choose_action(self, state):
        return 0

    def update(self, state, action, reward, next_state, done):
        return None


class OneStepEnv:
    def reset(self):
        return 0

    def step(self, action):
        return 1, 2.0, True, {}


def test_trainer_calls_episode_callback_with_run_id():
    events = []
    trainer = Trainer(FakeAgent(), OneStepEnv(), task_id=3, run_id="run-3")

    result = trainer.run(
        episodes=2,
        on_episode=lambda task_id, run_id, episode, reward, epsilon: events.append(
            (task_id, run_id, episode, reward, epsilon)
        ),
    )

    assert result is None
    assert events == [(3, "run-3", 0, 2.0, 0.7), (3, "run-3", 1, 2.0, 0.7)]


def test_trainer_returns_pause_when_control_callback_requests_pause():
    trainer = Trainer(FakeAgent(), OneStepEnv(), task_id=3, run_id="run-3")

    result = trainer.run(episodes=2, on_control=lambda task_id, episode, stage: "pause")

    assert result == "pause"


def test_trainer_returns_cancel_when_control_callback_requests_cancel_during_step():
    calls = []

    def on_control(task_id, episode, stage):
        calls.append(stage)
        return "cancel" if stage == "step" else None

    trainer = Trainer(FakeAgent(), OneStepEnv(), task_id=3, run_id="run-3")

    result = trainer.run(episodes=2, on_control=on_control)

    assert result == "cancel"
    assert calls == ["episode_start", "step"]
