import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from config import REDIS_URL
import redis

router = APIRouter()


@router.websocket("/ws/{task_id}")
async def websocket_reward_stream(websocket: WebSocket, task_id: int):
    await websocket.accept()
    r = redis.Redis.from_url(REDIS_URL)
    stream_key = f"task:{task_id}:reward_stream"
    last_id = "0"

    try:
        while True:
            entries = r.xread({stream_key: last_id}, count=10, block=2000)
            if entries:
                for _stream_name, messages in entries:
                    for msg_id, fields in messages:
                        last_id = msg_id
                        await websocket.send_json({
                            "type": "reward_update",
                            "episode": int(fields.get(b"episode", fields.get("episode", 0))),
                            "reward": float(fields.get(b"reward", fields.get("reward", 0))),
                            "epsilon": float(fields.get(b"epsilon", fields.get("epsilon", 0))),
                        })
            else:
                await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        r.close()