from pathlib import Path
import pytest
from gateos_manager.manifest.loader import load_manifest, ManifestValidationError

SCHEMA = Path("gateos_manager/manifest/schemas/environment-manifest-v1.0.yaml")

def make_manifest(tmp_path, content: str) -> Path:
    p = tmp_path / "test.yaml"
    p.write_text(content)
    return p

def test_schema_version_valid(tmp_path):
    manifest = make_manifest(
        tmp_path,
        """
kind: Environment
schemaVersion: "1.0"
metadata:
  name: validenv
spec:
  containers:
    - name: c1
      image: example/image:latest
"""
    )
    data = load_manifest(manifest, SCHEMA)
    assert data["metadata"]["name"] == "validenv"

def test_schema_version_missing(tmp_path):
    manifest = make_manifest(
        tmp_path,
        """
kind: Environment
metadata:
  name: noversion
spec:
  containers:
    - name: c1
      image: example/image:latest
"""
    )
    # Should still validate using provided schema
    data = load_manifest(manifest, SCHEMA)
    assert data["metadata"]["name"] == "noversion"

def test_schema_version_unsupported(tmp_path):
    manifest = make_manifest(
        tmp_path,
        """
kind: Environment
schemaVersion: "9.9"
metadata:
  name: badver
spec:
  containers:
    - name: c1
      image: example/image:latest
"""
    )
    with pytest.raises(ManifestValidationError) as e:
        load_manifest(manifest, SCHEMA)
    assert "Unsupported manifest schemaVersion" in str(e.value)
