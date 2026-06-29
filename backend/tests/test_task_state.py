import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.task_state import can_start_task, is_terminal_status, is_valid_control_command, normalize_status


class TaskStateTests(unittest.TestCase):
    def test_can_start_task_allows_pending_paused_and_failed(self):
        self.assertTrue(can_start_task("pending"))
        self.assertTrue(can_start_task("paused"))
        self.assertTrue(can_start_task("failed"))

    def test_can_start_task_rejects_running_and_completed(self):
        self.assertFalse(can_start_task("running"))
        self.assertFalse(can_start_task("completed"))

    def test_is_terminal_status(self):
        self.assertTrue(is_terminal_status("completed"))
        self.assertTrue(is_terminal_status("failed"))
        self.assertTrue(is_terminal_status("canceled"))
        self.assertFalse(is_terminal_status("running"))

    def test_normalize_status_rejects_unknown_value(self):
        with self.assertRaises(ValueError) as ctx:
            normalize_status("mystery")
        self.assertIn("Unsupported task status", str(ctx.exception))

    def test_control_command_detection(self):
        self.assertTrue(is_valid_control_command("pause"))
        self.assertTrue(is_valid_control_command("cancel"))
        self.assertTrue(is_valid_control_command("resume"))
        self.assertFalse(is_valid_control_command("running"))


if __name__ == "__main__":
    unittest.main()
