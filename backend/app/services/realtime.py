"""
Lightweight in-process broadcaster for order events (SSE/WebSocket friendly)
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List


class OrderEventBroadcaster:
    _subscribers: List[asyncio.Queue] = []

    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        cls._subscribers.append(queue)
        return queue

    @classmethod
    def unsubscribe(cls, queue: asyncio.Queue) -> None:
        try:
            cls._subscribers.remove(queue)
        except ValueError:
            pass

    @classmethod
    def publish(cls, event: Dict[str, Any]) -> None:
        # Non-blocking broadcast
        for queue in list(cls._subscribers):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Drop if consumer is slow
                continue



