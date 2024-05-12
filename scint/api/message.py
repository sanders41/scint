from __future__ import annotations

import json
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from scint.base.app import Scint
from scint.support.types import Dict, Message
from scint.support.logging import log

router = APIRouter()


@router.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            message = await receive(websocket)
            await send(websocket, message)

        except Exception as e:
            traceback_details = traceback.format_exc()
            log.error(f"Exception: {e}\n{traceback_details}")
            break

        except WebSocketDisconnect:
            break


async def receive(websocket: WebSocket):
    message = await websocket.receive_text()
    message = json.loads(message)
    log.debug(f"Message: {message}")
    return message


async def send(websocket: WebSocket, message: Dict[str, str]):
    async for res in Scint().parse(Message(**message)):
        if isinstance(res, Message):
            response = {"role": res.role, "content": str(res.content)}
            log.debug(f"Response: {response}")
            return await websocket.send_text(json.dumps(response))