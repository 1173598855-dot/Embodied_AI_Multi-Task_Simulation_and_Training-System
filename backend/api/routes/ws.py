import asyncio
import redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import REDIS_URL

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def websocket_reward_stream(websocket: WebSocket, task_id: int):
    await websocket.accept()
    r = redis.Redis.from_url(REDIS_URL)
    stream_key = f"task:{task_id}:events"
    last_id = "0"

    try:
        while True:
            entries = r.xread({stream_key: last_id}, count=10, block=2000)
            if entries:
                for _stream_name, messages in entries:
                    for msg_id, fields in messages:
                        last_id = msg_id
                        payload = {key.decode() if isinstance(key, bytes) else str(key): value for key, value in fields.items()}
                        event_type = payload.get("type", "reward_update")
                        if event_type == "reward_update":
                            await websocket.send_json(
                                {
                                    "type": "reward_update",
                                    "episode": int(payload.get("episode", 0)),
                                    "reward": float(payload.get("reward", 0)),
                                    "epsilon": float(payload.get("epsilon", 0)),
                                }
                            )
                        elif event_type == "status_change":
                            await websocket.send_json(
                                {
                                    "type": "status_change",
                                    "status": payload.get("status", "unknown"),
                                    "stage": payload.get("stage"),
                                    "episode": int(payload.get("episode", 0)) if payload.get("episode") is not None else None,
                                }
                            )
                        else:
                            await websocket.send_json({"type": event_type, **payload})
            else:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        r.close()
