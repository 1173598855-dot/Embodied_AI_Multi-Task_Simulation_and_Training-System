import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fakeredis

from app.domain.task_state import ControlCommand
from app.infrastructure.redis.control import TaskControl
from app.infrastructure.redis.events import EventStream
from app.infrastructure.redis.queue import QueuedTaskMessage, TaskQueue


def test_queue_round_trip_uses_structured_message():
    redis_client = fakeredis.FakeRedis()
    queue = TaskQueue(redis_client=redis_client)

    queue.enqueue(task_id=7, run_id="run-7", attempt=2)

    assert queue.size() == 1
    message = queue.dequeue()
    assert message == QueuedTaskMessage(task_id=7, run_id="run-7", attempt=2)
    assert queue.dequeue() is None


def test_queue_rejects_malformed_json_message():
    redis_client = fakeredis.FakeRedis()
    redis_client.lpush("embodied_ai:task_queue", "not-json")
    queue = TaskQueue(redis_client=redis_client)

    assert queue.dequeue() is None


def test_event_stream_publishes_and_reads_task_events():
    redis_client = fakeredis.FakeRedis()
    stream = EventStream(redis_client=redis_client)

    stream.publish(3, {"type": "status_changed", "task_id": 3, "status": "running"})
    entries = stream.read(task_id=3, last_id="0", count=10, block_ms=1)

    assert len(entries) == 1
    event_id, fields = entries[0]
    assert event_id
    assert fields["type"] == "status_changed"
    assert fields["status"] == "running"


def test_task_control_validates_and_clears_commands():
    redis_client = fakeredis.FakeRedis()
    control = TaskControl(redis_client=redis_client)

    control.set_command(5, ControlCommand.pause)
    assert control.get_command(5) == ControlCommand.pause
    control.clear_command(5)
    assert control.get_command(5) is None
