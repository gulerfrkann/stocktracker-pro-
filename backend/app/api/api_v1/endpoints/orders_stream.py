"""
Simple Server-Sent Events (SSE) endpoint for order events
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.services.realtime import OrderEventBroadcaster


router = APIRouter()


async def event_generator(queue: asyncio.Queue) -> AsyncGenerator[bytes, None]:
    try:
        while True:
            event = await queue.get()
            data = json.dumps(event)
            yield f"data: {data}\n\n".encode("utf-8")
    finally:
        OrderEventBroadcaster.unsubscribe(queue)


@router.get("/events/stream")
async def stream_events():
    queue = OrderEventBroadcaster.subscribe()
    return StreamingResponse(event_generator(queue), media_type="text/event-stream")



