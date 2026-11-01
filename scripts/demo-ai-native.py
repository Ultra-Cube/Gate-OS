#!/usr/bin/env python3
"""Offline Gate-OS/Ultra AI contract demo; no network or model is used."""
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(__file__).parents[1]
sys.path.insert(0, str(root))

from gateos_manager.ai_native import NativeShellPolicy, UiSpecSession

schema = json.loads((root / "schemas/ui-spec.schema.json").read_text())
spec = {
    "schemaVersion": "gateos.ui.v1",
    "id": "business-dashboard",
    "title": "Business dashboard",
    "layout": "dashboard",
    "theme": "system",
    "tiles": [
        {"id": "news", "component": "list", "label": "News", "dataBinding": "news.topic", "actions": ["refresh"]},
        {"id": "stocks", "component": "metric", "label": "Watchlist", "dataBinding": "markets.watchlist", "actions": ["open"]},
    ],
}
policy = NativeShellPolicy()
session = UiSpecSession(policy)
print(json.dumps(session.preview(spec, schema), indent=2))
session.accept(spec, schema)
print(json.dumps({"active": session.active["id"], "audit_events": len(policy.audit_log)}))
session.revert()
print(json.dumps({"active_after_revert": session.active}))
