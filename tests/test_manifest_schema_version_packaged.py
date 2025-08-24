from pathlib import Path

import pytest
import yaml

from gateos_manager.manifest.loader import ManifestValidationError, load_manifest

SCHEMA = Path("docs/architecture/schemas/environment-manifest.schema.yaml")


def _write_manifest(tmp_path, extra: dict, version: str | None = None):
    base = {
        "apiVersion": "gateos.ultracube.v1alpha1",
        "kind": "Environment",
        "metadata": {"name": "verpkg"},
        "spec": {"profile": {"category": "dev"}, "containers": [{"name": "c01", "image": "img"}]},
    }
    if version:
        base["schemaVersion"] = version
    base.update(extra)
    return yaml.safe_dump(base, sort_keys=False)


def test_packaged_schema_supported_version(tmp_path):
    m = tmp_path / "m.yaml"
    m.write_text(_write_manifest(tmp_path, {}, version="1.0"))
    data = load_manifest(m, SCHEMA)
    assert data["metadata"]["name"] == "verpkg"


def test_packaged_schema_unsupported_version(tmp_path):
    m = tmp_path / "m2.yaml"
    m.write_text(_write_manifest(tmp_path, {}, version="9.9"))
    with pytest.raises(ManifestValidationError):
        load_manifest(m, SCHEMA)
