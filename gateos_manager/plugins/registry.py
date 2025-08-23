"""Simple plugin registry scaffold.

Plugins register via entrypoint function call at import time. Future work:
 - Discovery via entry points / manifest
 - Lifecycle hooks (init, pre_switch, post_switch)
"""
from __future__ import annotations

from typing import Callable, Dict, List

Hook = Callable[..., None]

_hooks: Dict[str, List[Hook]] = {
    "pre_switch": [],
    "post_switch": [],
}


def register(hook_type: str, fn: Hook) -> None:
    if hook_type not in _hooks:  # pragma: no cover - defensive
        _hooks[hook_type] = []
    _hooks[hook_type].append(fn)


def invoke(hook_type: str, **ctx) -> None:  # pragma: no cover - IO side effects
    for fn in list(_hooks.get(hook_type, [])):
        try:
            fn(**ctx)
        except Exception:  # noqa: BLE001
            continue


def list_hooks() -> dict[str, int]:
    return {k: len(v) for k, v in _hooks.items()}
