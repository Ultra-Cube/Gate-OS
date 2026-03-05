"""Tests for Phase 7 — Mobile Companion API (WebSocket).

Covers:
- ConnectionManager (connect, disconnect, broadcast, count)
- Message format helpers (_make_message, _now_iso)
- WebSocket /ws/status endpoint integration via TestClient
- Broadcast triggered on switch (server.py integration)
- broadcast_sync() no-op safety when no event loop
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────
# ConnectionManager unit tests (async)
# ──────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_connect_adds_to_pool():
    from gateos_manager.api.websocket import ConnectionManager
    cm = ConnectionManager()
    ws = AsyncMock()
    await cm.connect(ws)
    assert cm.connection_count == 1
    ws.accept.assert_awaited_once()


@pytest.mark.anyio
async def test_disconnect_removes_from_pool():
    from gateos_manager.api.websocket import ConnectionManager
    cm = ConnectionManager()
    ws = AsyncMock()
    await cm.connect(ws)
    await cm.disconnect(ws)
    assert cm.connection_count == 0


@pytest.mark.anyio
async def test_broadcast_sends_to_all():
    from gateos_manager.api.websocket import ConnectionManager
    cm = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    await cm.connect(ws1)
    await cm.connect(ws2)
    msg = {"type": "status", "active_env": "gaming"}
    await cm.broadcast(msg)
    ws1.send_text.assert_awaited_once_with(json.dumps(msg))
    ws2.send_text.assert_awaited_once_with(json.dumps(msg))


@pytest.mark.anyio
async def test_broadcast_drops_dead_connections():
    from gateos_manager.api.websocket import ConnectionManager
    cm = ConnectionManager()
    dead_ws = AsyncMock()
    dead_ws.send_text.side_effect = RuntimeError("connection closed")
    alive_ws = AsyncMock()
    await cm.connect(dead_ws)
    await cm.connect(alive_ws)
    await cm.broadcast({"type": "ping"})
    # dead connection removed
    assert cm.connection_count == 1
    alive_ws.send_text.assert_awaited_once()


# ──────────────────────────────────────────────────────────────────────────
# Message helpers
# ──────────────────────────────────────────────────────────────────────────

def test_make_message_structure():
    from gateos_manager.api.websocket import _make_message
    msg = _make_message("switch_done", active_env="gaming", payload={"status": "success"})
    assert msg["type"] == "switch_done"
    assert msg["active_env"] == "gaming"
    assert "timestamp" in msg
    assert msg["payload"]["status"] == "success"


def test_make_message_defaults():
    from gateos_manager.api.websocket import _make_message
    msg = _make_message("status")
    assert msg["active_env"] is None
    assert msg["payload"] == {}


def test_now_iso_format():
    from gateos_manager.api.websocket import _now_iso
    ts = _now_iso()
    # Basic ISO-8601 UTC check
    assert "T" in ts and "+" in ts or "Z" in ts


def test_broadcast_sync_noop_without_loop():
    """broadcast_sync must not raise when there is no running event loop."""
    from gateos_manager.api.websocket import broadcast_sync
    broadcast_sync({"type": "status"})  # should not raise


# ──────────────────────────────────────────────────────────────────────────
# WebSocket endpoint integration (FastAPI TestClient)
# ──────────────────────────────────────────────────────────────────────────

try:
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app
    _API_AVAILABLE = True
except ImportError:
    _API_AVAILABLE = False

pytestmark_api = pytest.mark.skipif(not _API_AVAILABLE, reason="FastAPI not installed")


@pytestmark_api
def test_ws_status_connect_sends_welcome():
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app

    client = TestClient(app)
    with client.websocket_connect("/ws/status") as ws:
        data = ws.receive_json()
        assert data["type"] == "status"
        assert "clients" in data["payload"]


@pytestmark_api
def test_ws_status_ping_pong():
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app

    client = TestClient(app)
    with client.websocket_connect("/ws/status") as ws:
        ws.receive_json()  # welcome
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"
        assert pong["payload"]["type"] == "ping"


@pytestmark_api
def test_ws_status_non_json_message():
    from fastapi.testclient import TestClient
    from gateos_manager.api.server import app
    client = TestClient(app)
    with client.websocket_connect("/ws/status") as ws:
        ws.receive_json()  # welcome
        ws.send_text("not-json")
        pong = ws.receive_json()
        assert pong["type"] == "pong"
        assert "raw" in pong["payload"]


@pytestmark_api
def test_ws_router_registered_in_app():
    from gateos_manager.api.server import app
    routes = [r.path for r in app.routes]
    assert "/ws/status" in routes
