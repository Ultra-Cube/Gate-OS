from pathlib import Path

import pytest

from gateos_manager.manifest.loader import ManifestValidationError, load_manifest

SCHEMA = Path("docs/architecture/schemas/environment-manifest.schema.yaml")

def test_manifest_without_schema_version_uses_provided_schema(tmp_path):
    m = tmp_path / "env.yaml"
    m.write_text(
    """apiVersion: gateos.ultracube.v1alpha1\nkind: Environment\nmetadata:\n  name: devx\nspec:\n  profile:\n    category: dev\n  containers:\n    - name: core\n      image: x/y:1\n"""
    )
    data = load_manifest(m, SCHEMA)
    assert data["metadata"]["name"] == "devx"

def test_manifest_with_supported_schema_version(tmp_path):
    m = tmp_path / "env2.yaml"
    m.write_text(
    """schemaVersion: "1.0"\napiVersion: gateos.ultracube.v1alpha1\nkind: Environment\nmetadata:\n  name: devy\nspec:\n  profile:\n    category: dev\n  containers:\n    - name: core\n      image: x/y:1\n"""
    )
    data = load_manifest(m, SCHEMA)
    assert data["metadata"]["name"] == "devy"

def test_manifest_with_unsupported_schema_version(tmp_path):
    m = tmp_path / "env3.yaml"
    m.write_text(
    """schemaVersion: "9.9"\napiVersion: gateos.ultracube.v1alpha1\nkind: Environment\nmetadata:\n  name: badver\nspec:\n  profile:\n    category: dev\n  containers:\n    - name: core\n      image: x/y:1\n"""
    )
    with pytest.raises(ManifestValidationError):
        load_manifest(m, SCHEMA)
