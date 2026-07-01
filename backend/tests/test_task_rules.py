import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.domain.task_rules import can_cancel, can_delete, can_pause, can_start, is_terminal
from app.domain.task_state import TaskStatus


def test_start_rules_match_enterprise_state_model():
    allowed = {TaskStatus.created, TaskStatus.paused, TaskStatus.failed}
    for status in TaskStatus:
        assert can_start(status) is (status in allowed)


def test_pause_rules_match_enterprise_state_model():
    allowed = {TaskStatus.queued, TaskStatus.running}
    for status in TaskStatus:
        assert can_pause(status) is (status in allowed)


def test_cancel_rules_match_enterprise_state_model():
    allowed = {
        TaskStatus.created,
        TaskStatus.queued,
        TaskStatus.running,
        TaskStatus.paused,
        TaskStatus.failed,
    }
    for status in TaskStatus:
        assert can_cancel(status) is (status in allowed)


def test_delete_rules_match_enterprise_state_model():
    allowed = {TaskStatus.created, TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}
    for status in TaskStatus:
        assert can_delete(status) is (status in allowed)


def test_terminal_rules_match_enterprise_state_model():
    terminal = {TaskStatus.completed, TaskStatus.failed, TaskStatus.canceled}
    for status in TaskStatus:
        assert is_terminal(status) is (status in terminal)
