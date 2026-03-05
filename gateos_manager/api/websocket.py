"""
gateos_manager.api.websocket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
WebSocket endpoint for real-time Gate-OS status streaming.

Clients connect to ``ws://<host>:<port>/ws/status`` and receive JSON
messages whenever the active environment changes or a switch is in progress.

Message schema (JSON):
    {
        "type": "status",          // "status" | "switch_start" | "switch_done" | "error"
        "active_env": "gaming",    // currently active environment name (or null)
        "timestamp": "2026-...",   // ISO-8601 UTC
        "payload": { ... }         // optional extra data
    }

The module exposes:
    broadcast(message: dict)   — send a message to all connected clients
    router                     — FastAPI APIRouter to include in the main app
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Mobile / WebSocket"])

# ── Connection manager ─────────────────────────────────────────────────────


class ConnectionManager:
    """Tracks all active WebSocket connections and supports broadcast."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections = [c for c in self._connections if c is not ws]

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send *message* to all connected clients; drop dead connections."""
        text = json.dumps(message)
        dead: list[WebSocket] = []
        async with self._lock:
            targets = list(self._connections)
        for ws in targets:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


manager = ConnectionManager()


# ── Helper ─────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_message(
    msg_type: str,
    active_env: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "type": msg_type,
        "active_env": active_env,
        "timestamp": _now_iso(),
        "payload": payload or {},
    }


# Module-level convenience wrapper (sync-friendly via asyncio.run / create_task)
def broadcast_sync(message: dict[str, Any]) -> None:
    """Fire-and-forget broadcast from synchronous code.

    Creates a new event loop task if one is running, otherwise is a no-op.
    Safe to call from non-async contexts.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(message))
    except RuntimeError:
        pass  # No event loop — skip broadcast


# ── Endpoint ───────────────────────────────────────────────────────────────

@router.websocket("/ws/status")
async def ws_status(ws: WebSocket) -> None:
    """WebSocket endpoint — streams Gate-OS environment status to the client.

    On connect: sends current connected-clients count.
    On any client message: echoes it back as a ``ping``/``pong`` pair.
    On disconnect: client is removed from the pool.
    """
    await manager.connect(ws)
    try:
        # Welcome message
        await ws.send_text(json.dumps(_make_message(
            "status",
            payload={"info": "connected", "clients": manager.connection_count},
        )))
        while True:
            # Keep connection alive; handle optional client messages
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                msg = {"raw": data}
            # Echo back as pong
            await ws.send_text(json.dumps(_make_message("pong", payload=msg)))
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(ws)
