"""Simple plugin registry scaffold.

Plugins register via entrypoint function call at import time. Future work:
 - Discovery via entry points / manifest
 - Lifecycle hooks (init, pre_switch, post_switch)
"""
from __future__ import annotations

from typing import Callable, Dict, List
from importlib import metadata
import os

Hook = Callable[..., None]

_hooks: Dict[str, List[Hook]] = {
    "pre_switch": [],
    "post_switch": [],
    "shutdown": [],  # invoked on manager shutdown (future) or switch failure cleanup
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


def discover_entrypoint_plugins(group: str = 'gateos.plugins') -> list:
    """Discover and load plugins via entry points.

    Each entry point should reference a callable that, when imported, registers hooks.
    Returns a list of loaded plugin callables. Safe to call multiple times (idempotent best effort).
    Opt-out by setting env GATEOS_DISABLE_ENTRYPOINT_PLUGINS=1.
    """
    if os.getenv('GATEOS_DISABLE_ENTRYPOINT_PLUGINS') == '1':  # pragma: no cover - opt out path
        return []
    plugins = []
    try:  # pragma: no cover - metadata scanning
        for ep in metadata.entry_points().select(group=group):
            try:
                plugin = ep.load()  # side-effect: registration
                plugins.append(plugin)
            except Exception:
                continue
    except Exception:
        return plugins
    return plugins
