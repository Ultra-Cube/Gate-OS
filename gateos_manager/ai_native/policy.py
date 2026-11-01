"""Local policy boundary for declarative AI-generated UI proposals."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from jsonschema import Draft202012Validator, ValidationError


class PolicyDenied(ValueError):
    """Raised when a proposed AI action exceeds the local policy."""


@dataclass(frozen=True)
class AuditEvent:
    event: str
    subject: str
    detail: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NativeShellPolicy:
    """Allow only schema-valid, pre-approved native UI components."""

    allowed_components = frozenset({"text", "metric", "list", "calendar", "status"})
    allowed_actions = frozenset({"refresh", "open", "approve", "dismiss"})

    def __init__(self) -> None:
        self.audit_log: list[AuditEvent] = []

    def validate_ui_spec(self, spec: dict[str, Any], schema: dict[str, Any]) -> None:
        try:
            Draft202012Validator(schema).validate(spec)
        except ValidationError as exc:
            raise PolicyDenied(f"UI spec rejected by schema: {exc.message}") from exc
        for tile in spec["tiles"]:
            if tile["component"] not in self.allowed_components:
                raise PolicyDenied(f"component not approved: {tile['component']}")
            if set(tile.get("actions", ())) - self.allowed_actions:
                raise PolicyDenied(f"action not approved in tile: {tile['id']}")
        self.audit_log.append(AuditEvent("ui_spec.validated", spec["id"]))


class UiSpecSession:
    """Preview, accept, and revert a UI proposal without executing model code."""

    def __init__(self, policy: NativeShellPolicy) -> None:
        self.policy = policy
        self._active: dict[str, Any] | None = None
        self._previous: dict[str, Any] | None = None

    @property
    def active(self) -> dict[str, Any] | None:
        return self._active

    def preview(self, spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
        self.policy.validate_ui_spec(spec, schema)
        self.policy.audit_log.append(AuditEvent("ui_spec.previewed", spec["id"]))
        return {"status": "preview", "id": spec["id"], "components": [t["component"] for t in spec["tiles"]]}

    def accept(self, spec: dict[str, Any], schema: dict[str, Any]) -> None:
        self.policy.validate_ui_spec(spec, schema)
        self._previous = self._active
        self._active = dict(spec)
        self.policy.audit_log.append(AuditEvent("ui_spec.accepted", spec["id"]))

    def revert(self) -> None:
        if self._active is None:
            raise PolicyDenied("no accepted UI spec to revert")
        current_id = self._active["id"]
        self._active = self._previous
        self._previous = None
        self.policy.audit_log.append(AuditEvent("ui_spec.reverted", current_id))
