import json
from pathlib import Path

import pytest

from gateos_manager.ai_native import NativeShellPolicy, PolicyDenied, UiSpecSession

ROOT = Path(__file__).parents[1]
SCHEMA = json.loads((ROOT / "schemas/ui-spec.schema.json").read_text())


def valid_spec(identifier="business-dashboard"):
    return {
        "schemaVersion": "gateos.ui.v1",
        "id": identifier,
        "title": "Business dashboard",
        "layout": "dashboard",
        "theme": "system",
        "tiles": [
            {"id": "market", "component": "metric", "label": "Market", "dataBinding": "market.index", "actions": ["refresh"]},
            {"id": "agenda", "component": "calendar", "label": "Agenda", "actions": ["open"]},
        ],
    }


def test_preview_accept_and_revert_are_audited():
    policy = NativeShellPolicy()
    session = UiSpecSession(policy)
    assert session.preview(valid_spec(), SCHEMA)["status"] == "preview"
    session.accept(valid_spec(), SCHEMA)
    assert session.active["id"] == "business-dashboard"
    session.accept(valid_spec("second-dashboard"), SCHEMA)
    session.revert()
    assert session.active["id"] == "business-dashboard"
    assert [event.event for event in policy.audit_log] == [
        "ui_spec.validated", "ui_spec.previewed", "ui_spec.validated",
        "ui_spec.accepted", "ui_spec.validated", "ui_spec.accepted", "ui_spec.reverted",
    ]


def test_unknown_component_is_denied():
    spec = valid_spec()
    spec["tiles"][0]["component"] = "arbitrary_webview"
    with pytest.raises((PolicyDenied, ValueError)):
        UiSpecSession(NativeShellPolicy()).preview(spec, SCHEMA)


def test_schema_rejects_extra_executable_fields():
    spec = valid_spec()
    spec["execute"] = "rm -rf /"
    with pytest.raises(ValueError):
        UiSpecSession(NativeShellPolicy()).preview(spec, SCHEMA)
