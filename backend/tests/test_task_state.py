import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.domain.task_state import ControlCommand, TaskStatus


def test_task_status_values_are_stable_api_strings():
    assert [status.value for status in TaskStatus] == [
        "created",
        "queued",
        "running",
        "paused",
        "completed",
        "failed",
        "canceled",
    ]


def test_control_command_values_are_limited_to_worker_commands():
    assert [command.value for command in ControlCommand] == ["pause", "cancel"]
