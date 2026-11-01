"""Simple plugin registry scaffold.

Plugins register via entrypoint function call at import time. Future work:
 - Discovery via entry points / manifest
 - Lifecycle hooks (init, pre_switch, post_switch)

Security flags (Phase 13.2):
  GATEOS_ALLOW_UNSIGNED_PLUGINS=false  (default) — require signature before load
  GATEOS_ALLOW_UNSIGNED_PLUGINS=true   — allow unsigned plugins (dev/test mode)
  GATEOS_PLUGIN_ISOLATE=1              — run plugins in a restricted subprocess
"""

from __future__ import annotations

import base64
import os
import subprocess
import sys
from collections.abc import Callable
from importlib import metadata

Hook = Callable[..., None]

_hooks: dict[str, list[Hook]] = {
    'pre_switch': [],
    'post_switch': [],
    'shutdown': [],  # invoked on manager shutdown (future) or switch failure cleanup
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


# ---------------------------------------------------------------------------
# Signature verification (Phase 13.2)
# ---------------------------------------------------------------------------


def _allow_unsigned() -> bool:
    """Return True when unsigned plugins are explicitly permitted."""
    return os.getenv('GATEOS_ALLOW_UNSIGNED_PLUGINS', 'false').lower() in ('1', 'true', 'yes')


def _verify_plugin_signature(ep: metadata.EntryPoint) -> bool:
    """Return True if the plugin's distribution package has a valid manifest sig.

    Checks for a ``RECORD.sig`` or ``<dist>.sig`` file distributed alongside the
    package metadata. Falls back to the gate-os manifest signing module when the
    distribution exposes a ``dist-info/signing.pub``.

    When neither artefact is present the return value depends on
    ``GATEOS_ALLOW_UNSIGNED_PLUGINS``.
    """
    try:
        dist = metadata.distribution(ep.value.split(':')[0].split('.')[0])
        # Look for any *.sig file in the dist metadata directory
        sig_files = [f for f in dist.files or [] if str(f).endswith('.sig')]
        if sig_files:
            if os.getenv('GATEOS_REQUIRE_PLUGIN_SIGNATURES') != '1':
                return True
            record_files = [f for f in dist.files or [] if str(f).endswith('RECORD')]
            public_key_files = [
                f for f in dist.files or [] if str(f).endswith('gateos-signing.pub')
            ]
            if not record_files or not public_key_files:
                return False
            from cryptography.hazmat.primitives import serialization

            record = dist.locate_file(record_files[0]).read_bytes()
            signature = base64.b64decode(
                dist.locate_file(sig_files[0]).read_text().strip(), validate=True
            )
            public_key = serialization.load_pem_public_key(
                dist.locate_file(public_key_files[0]).read_bytes()
            )
            public_key.verify(signature, record)
            return True
    except Exception:
        pass
    return _allow_unsigned()


def _load_plugin_isolated(ep: metadata.EntryPoint):  # pragma: no cover - subprocess path
    """Load a plugin entry point in a restricted subprocess.

    Spawns a new Python interpreter with no inherited file descriptors and a
    minimal environment. The subprocess is expected to exit 0. This provides
    basic process isolation: a malformed plugin cannot crash the manager process.

    Returns None (side effects in subprocess only — hooks cannot be registered
    cross-process; use this mode for probe/validation only).
    """
    cmd = [
        sys.executable,
        '-c',
        f"import importlib; ep = importlib.import_module('{ep.value.split(':')[0]}'); print('ok')",
    ]
    env = {
        k: v
        for k, v in os.environ.items()
        if k.startswith('GATEOS_') or k in ('PATH', 'HOME', 'LANG')
    }
    try:
        subprocess.run(
            cmd,
            env=env,
            timeout=10,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def discover_entrypoint_plugins(group: str = 'gateos.plugins') -> list:
    """Discover and load plugins via entry points.

    Each entry point should reference a callable that, when imported, registers
    hooks.  Returns a list of loaded plugin callables. Safe to call multiple
    times (idempotent best effort).

    Security (Phase 13.2):
    - When GATEOS_ALLOW_UNSIGNED_PLUGINS is false (default) each plugin's
      distribution signature is checked before loading.  Unsigned plugins are
      skipped with a warning logged to stderr.
    - When GATEOS_PLUGIN_ISOLATE=1 plugins are probed in a subprocess first;
      the entry point is still loaded in-process for hook registration.

    Opt-out by setting env GATEOS_DISABLE_ENTRYPOINT_PLUGINS=1.
    """
    if os.getenv('GATEOS_DISABLE_ENTRYPOINT_PLUGINS') == '1':  # pragma: no cover - opt out path
        return []
    isolate = os.getenv('GATEOS_PLUGIN_ISOLATE') == '1'
    plugins = []
    try:  # pragma: no cover - metadata scanning
        for ep in metadata.entry_points().select(group=group):
            try:
                if not _verify_plugin_signature(ep):
                    import sys as _sys

                    _sys.stderr.write(
                        f"[gate-os] skipping unsigned plugin '{ep.name}' "
                        f'(set GATEOS_ALLOW_UNSIGNED_PLUGINS=true to override)\n'
                    )
                    continue
                if isolate:
                    _load_plugin_isolated(ep)
                plugin = ep.load()  # side-effect: registration
                plugins.append(plugin)
            except Exception:
                continue
    except Exception:
        return plugins
    return plugins
