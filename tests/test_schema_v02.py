"""Tests for schema v0.2.0 (allowlistRef, networkNamespace) and migration hook."""
from __future__ import annotations

from pathlib import Path

import pytest

from gateos_manager.manifest.loader import (
    ManifestValidationError,
    _migrate_v1_to_v02,
    load_manifest,
)

SCHEMA_V1 = Path("gateos_manager/manifest/schemas/environment-manifest-v1.0.yaml")
SCHEMA_V02 = Path("gateos_manager/manifest/schemas/environment-manifest-v0.2.0.yaml")


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "manifest.yaml"
    p.write_text(content)
    return p


# ── Schema v0.2.0 basic validation ────────────────────────────────────────────

def test_schema_v02_valid_minimal(tmp_path):
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "0.2.0"
metadata:
  name: testenv
spec:
  containers:
    - name: c1
      image: example/image:latest
""")
    data = load_manifest(p, SCHEMA_V02)
    assert data["metadata"]["name"] == "testenv"


def test_schema_v02_allowlist_ref(tmp_path):
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "0.2.0"
metadata:
  name: devenv
spec:
  containers:
    - name: c1
      image: example/dev:latest
      allowlistRef: "gateos-dev-allowlist"
      networkNamespace: "gateos-dev-ns"
""")
    data = load_manifest(p, SCHEMA_V02)
    containers = data["spec"]["containers"]
    assert containers[0]["allowlistRef"] == "gateos-dev-allowlist"
    assert containers[0]["networkNamespace"] == "gateos-dev-ns"


def test_schema_v02_power_profile_field(tmp_path):
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "0.2.0"
metadata:
  name: gamingenv
spec:
  profile:
    category: gaming
    performance:
      cpuGovernor: performance
      gpuMode: performance
      powerProfile: performance
  containers:
    - name: c1
      image: example/gaming:latest
""")
    data = load_manifest(p, SCHEMA_V02)
    perf = data["spec"]["profile"]["performance"]
    assert perf["powerProfile"] == "performance"


def test_schema_v02_rejects_bad_cpu_governor(tmp_path):
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "0.2.0"
metadata:
  name: badenv
spec:
  profile:
    performance:
      cpuGovernor: turbo-max
  containers:
    - name: c1
      image: example/image:latest
""")
    with pytest.raises(ManifestValidationError):
        load_manifest(p, SCHEMA_V02)


def test_schema_v02_unsupported_version_raises(tmp_path):
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "9.9"
metadata:
  name: future
spec:
  containers: []
""")
    with pytest.raises(ManifestValidationError, match="Unsupported manifest schemaVersion"):
        load_manifest(p, SCHEMA_V02)


# ── Migration hook ─────────────────────────────────────────────────────────────

def test_migrate_v1_to_v02_sets_version():
    data = {
        "kind": "Environment",
        "schemaVersion": "1.0",
        "metadata": {"name": "x"},
        "spec": {"containers": [{"name": "c1", "image": "img:latest"}]},
    }
    result = _migrate_v1_to_v02(data)
    assert result["schemaVersion"] == "0.2.0"


def test_migrate_v1_to_v02_preserves_containers():
    data = {
        "kind": "Environment",
        "schemaVersion": "1.0",
        "metadata": {"name": "x"},
        "spec": {"containers": [{"name": "c1", "image": "img:latest"}]},
    }
    result = _migrate_v1_to_v02(data)
    # Containers are preserved unchanged
    assert result["spec"]["containers"][0]["name"] == "c1"


def test_migrate_v1_to_v02_preserves_existing_allowlist_fields():
    data = {
        "kind": "Environment",
        "schemaVersion": "1.0",
        "metadata": {"name": "x"},
        "spec": {
            "containers": [{
                "name": "c1",
                "image": "img:latest",
                "allowlistRef": "my-list",
                "networkNamespace": "my-ns",
            }]
        },
    }
    result = _migrate_v1_to_v02(data)
    c = result["spec"]["containers"][0]
    assert c["allowlistRef"] == "my-list"
    assert c["networkNamespace"] == "my-ns"


def test_migrate_v1_to_v02_is_non_destructive():
    """Original dict is not mutated."""
    data = {
        "kind": "Environment",
        "schemaVersion": "1.0",
        "metadata": {"name": "x"},
        "spec": {"containers": [{"name": "c1", "image": "img:latest"}]},
    }
    original_version = data["schemaVersion"]
    _migrate_v1_to_v02(data)
    assert data["schemaVersion"] == original_version


def test_migrate_v1_to_v02_no_containers():
    """Migration with no containers list does not crash."""
    data = {
        "kind": "Environment",
        "schemaVersion": "1.0",
        "metadata": {"name": "x"},
        "spec": {},
    }
    result = _migrate_v1_to_v02(data)
    assert result["schemaVersion"] == "0.2.0"


def test_load_manifest_auto_migrate(tmp_path):
    """auto_migrate=True upgrades v1.0 manifest and validates against v0.2.0 schema."""
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "1.0"
metadata:
  name: migrated
spec:
  containers:
    - name: c1
      image: example/image:latest
""")
    data = load_manifest(p, SCHEMA_V1, auto_migrate=True)
    assert data["schemaVersion"] == "0.2.0"
    assert data["metadata"]["name"] == "migrated"


def test_load_manifest_no_auto_migrate_v1_stays_v1(tmp_path):
    """Without auto_migrate, v1.0 manifest is validated against v1.0 schema unchanged."""
    p = _write(tmp_path, """
kind: Environment
schemaVersion: "1.0"
metadata:
  name: stable
spec:
  containers:
    - name: c1
      image: example/image:latest
""")
    data = load_manifest(p, SCHEMA_V1)
    assert data["schemaVersion"] == "1.0"
