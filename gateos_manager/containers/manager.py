"""Lightweight container orchestration abstraction.

This *minimal* implementation supports two modes:

1. Dry-run (default in tests) — no real runtime interaction, maintains in-memory state.
2. Runtime mode — attempts to invoke a container runtime (`podman` then fallback to `docker`).

Environment Variables:
 - GATEOS_CONTAINER_DRY_RUN=1  -> force dry-run (never execute subprocess)
 - GATEOS_CONTAINER_RUNTIME    -> explicit runtime binary name
 - GATEOS_SECURITY_ENFORCE=1   -> trigger isolation hooks (seccomp/AppArmor stubs)

Manifest Contract (subset expected):
{
  "name": "dev",  # optional, used to prefix container names
  "containers": [
     {
       "name": "redis",
       "image": "redis:7",
       "ports": ["6379:6379"],
       "env": {"FOO": "bar"},
       "mounts": [{"source": "/host/path", "target": "/ctr/path", "readOnly": false}]
     }
  ],
  "mounts": [   # top-level mounts applied to every container
     {"source": "/home/user/work", "target": "/workspace", "readOnly": false}
  ]
}

All operations are best-effort; failures emit telemetry/logs but do not raise unless critical.

Timeouts:
 - Container start: 30 s (GATEOS_CONTAINER_START_TIMEOUT env var overrides)
 - Container stop:  15 s (GATEOS_CONTAINER_STOP_TIMEOUT  env var overrides)
"""
from __future__ import annotations

import os
import shlex
import subprocess
import shutil
from typing import Any, Dict, List

_START_TIMEOUT = int(os.getenv('GATEOS_CONTAINER_START_TIMEOUT', '30'))
_STOP_TIMEOUT  = int(os.getenv('GATEOS_CONTAINER_STOP_TIMEOUT',  '15'))

from gateos_manager.logging.structured import info, warn, error
from gateos_manager.telemetry.emitter import emit
from gateos_manager.security.isolation import apply_isolation


class ContainerManager:
    def __init__(self, dry_run: bool | None = None, runtime: str | None = None) -> None:
        self._dry_run = (
            dry_run if dry_run is not None else os.getenv('GATEOS_CONTAINER_DRY_RUN') == '1'
        )
        self._runtime = (
            runtime or os.getenv('GATEOS_CONTAINER_RUNTIME') or self._detect_runtime()
        )
        self._state: Dict[str, str] = {}

    # ------------------------- public API ------------------------- #
    def start(self, manifest: dict[str, Any], correlation_id: str | None = None) -> List[str]:
        containers = manifest.get('containers') or []
        started: List[str] = []
        top_mounts: List[dict] = manifest.get('mounts') or []
        for spec in containers:
            cname = self._container_name(manifest, spec)
            if self._state.get(cname) == 'running':
                continue
            if self._start_single(cname, spec, manifest_name=manifest.get('name') or 'env',
                                  top_mounts=top_mounts, correlation_id=correlation_id):
                started.append(cname)
        return started

    def stop(self, manifest: dict[str, Any], correlation_id: str | None = None) -> List[str]:
        containers = manifest.get('containers') or []
        stopped: List[str] = []
        for spec in containers:
            cname = self._container_name(manifest, spec)
            if self._state.get(cname) != 'running':
                continue
            if self._stop_single(cname, correlation_id=correlation_id):
                stopped.append(cname)
        return stopped

    def status(self, manifest: dict[str, Any]) -> Dict[str, str]:
        containers = manifest.get('containers') or []
        return {self._container_name(manifest, c): self._state.get(self._container_name(manifest, c), 'unknown') for c in containers}

    # ------------------------- internals ------------------------- #
    def _detect_runtime(self) -> str:
        """Detect an available container runtime.

        Preference order: podman, docker. If neither is found, switch to dry-run
        mode and return 'none'.
        """
        for candidate in ('podman', 'docker'):
            if shutil.which(candidate):
                return candidate
        # Neither runtime found: enable dry-run fallback
        self._dry_run = True
        warn('container.runtime.missing', detail='podman/docker not found; switching to dry-run')
        return 'none'

    def _container_name(self, manifest: dict[str, Any], spec: dict[str, Any]) -> str:
        prefix = manifest.get('name') or 'env'
        return f'gateos_{prefix}_{spec.get("name", spec.get("image", "ctr"))}'

    def _start_single(
        self,
        cname: str,
        spec: dict[str, Any],
        *,
        manifest_name: str = 'env',
        top_mounts: List[dict] | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        image = spec.get('image')
        if not image:
            warn('container.skip.no_image', container=cname, correlation_id=correlation_id)
            return False
        emit('container.start.attempt', container=cname, image=image, correlation_id=correlation_id)
        info('container.start.attempt', container=cname, image=image, runtime=self._runtime, dry_run=self._dry_run, correlation_id=correlation_id)
        if self._dry_run:
            self._state[cname] = 'running'
            apply_isolation(cname, spec, correlation_id=correlation_id)
            emit('container.start', container=cname, status='running', dry_run=True, correlation_id=correlation_id)
            return True
        try:
            cmd = [self._runtime, 'run', '-d', '--name', cname,
                   '--label', f'gateos.env={manifest_name}',
                   '--label', 'gateos.managed=true']
            for k, v in (spec.get('env') or {}).items():
                cmd += ['-e', f'{k}={v}']
            for p in spec.get('ports', []):
                cmd += ['-p', p]
            # top-level mounts applied to every container
            for m in (top_mounts or []):
                flag = f"{m['source']}:{m['target']}"
                if m.get('readOnly'):
                    flag += ':ro'
                cmd += ['-v', flag]
            # per-container mounts override / extend
            for m in (spec.get('mounts') or []):
                flag = f"{m['source']}:{m['target']}"
                if m.get('readOnly'):
                    flag += ':ro'
                cmd += ['-v', flag]
            # isolation stubs (future: seccomp/AppArmor flags)
            apply_isolation(cname, spec, correlation_id=correlation_id)
            cmd.append(image)
            if spec.get('command'):
                cmd += shlex.split(spec['command'])
            result = subprocess.run(
                cmd, check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=_START_TIMEOUT,
            )
            if result.returncode != 0:
                stderr_out = result.stderr.decode(errors='replace').strip()
                error('container.start.runtime_error', container=cname,
                      returncode=result.returncode, stderr=stderr_out,
                      correlation_id=correlation_id)
                emit('container.start', container=cname, status='error',
                     returncode=result.returncode, correlation_id=correlation_id)
                return False
            self._state[cname] = 'running'
            emit('container.start', container=cname, status='running', correlation_id=correlation_id)
            return True
        except subprocess.TimeoutExpired:
            error('container.start.timeout', container=cname, timeout=_START_TIMEOUT,
                  correlation_id=correlation_id)
            emit('container.start', container=cname, status='timeout', correlation_id=correlation_id)
            return False
        except Exception as e:  # noqa: BLE001
            error('container.start.error', container=cname, error=str(e), correlation_id=correlation_id)
            emit('container.start', container=cname, status='error', error=str(e), correlation_id=correlation_id)
            return False

    def _stop_single(self, cname: str, correlation_id: str | None = None) -> bool:
        emit('container.stop.attempt', container=cname, correlation_id=correlation_id)
        if self._dry_run:
            self._state[cname] = 'stopped'
            emit('container.stop', container=cname, status='stopped', dry_run=True, correlation_id=correlation_id)
            return True
        try:
            result = subprocess.run(
                [self._runtime, 'stop', cname], check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                timeout=_STOP_TIMEOUT,
            )
            if result.returncode != 0:
                stderr_out = result.stderr.decode(errors='replace').strip()
                warn('container.stop.runtime_error', container=cname,
                     returncode=result.returncode, stderr=stderr_out,
                     correlation_id=correlation_id)
            # always attempt rm even if stop failed
            subprocess.run(
                [self._runtime, 'rm', '--force', cname], check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=_STOP_TIMEOUT,
            )
            self._state[cname] = 'stopped'
            emit('container.stop', container=cname, status='stopped', correlation_id=correlation_id)
            return True
        except subprocess.TimeoutExpired:
            error('container.stop.timeout', container=cname, timeout=_STOP_TIMEOUT,
                  correlation_id=correlation_id)
            emit('container.stop', container=cname, status='timeout', correlation_id=correlation_id)
            return False
        except Exception as e:  # noqa: BLE001
            error('container.stop.error', container=cname, error=str(e), correlation_id=correlation_id)
            emit('container.stop', container=cname, status='error', error=str(e), correlation_id=correlation_id)
            return False

