import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.application.training_log_service import TrainingLogService


class FakeLogRepository:
    def __init__(self):
        self.logs = {1: ["episode-1", "episode-2"]}

    def list_by_task(self, task_id):
        return self.logs.get(task_id, [])


def test_training_log_service_lists_logs_for_task():
    service = TrainingLogService(FakeLogRepository())

    assert service.list_logs(1) == ["episode-1", "episode-2"]
    assert service.list_logs(2) == []
