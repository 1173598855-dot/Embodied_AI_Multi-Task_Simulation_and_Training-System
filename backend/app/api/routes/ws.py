import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.deps import get_event_stream
from app.infrastructure.redis.events import EventStream

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{task_id}")
async def websocket_reward_stream(
    websocket: WebSocket,
    task_id: int,
    event_stream: EventStream = Depends(get_event_stream),
):
    await websocket.accept()
    last_id = "0"
    try:
        while True:
            entries = event_stream.read(task_id=task_id, last_id=last_id, count=10, block_ms=2000)
            for event_id, fields in entries:
                last_id = event_id
                event_type = fields.get("type", "episode_completed")
                if event_type == "episode_completed":
                    await websocket.send_json(
                        {
                            "type": "episode_completed",
                            "episode": int(fields.get("episode", 0)),
                            "reward": float(fields.get("reward", 0)),
                            "epsilon": float(fields.get("epsilon", 0)),
                            "avg_reward": float(fields.get("avg_reward", 0)),
                        }
                    )
                elif event_type == "status_changed":
                    await websocket.send_json({"type": "status_changed", "status": fields.get("status", "unknown")})
                else:
                    await websocket.send_json({"type": event_type, **fields})
            if not entries:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        return
