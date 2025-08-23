from pathlib import Path
import pytest

from gateos_manager.manifest.loader import (
    ManifestValidationError,
    load_manifest,
)


SCHEMA = Path("docs/architecture/schemas/environment-manifest.schema.yaml")
EXAMPLES = Path("examples/environments")


@pytest.mark.parametrize("manifest_path", list(EXAMPLES.glob("*.yaml")))
def test_example_manifests_validate(manifest_path: Path):
    data = load_manifest(manifest_path, SCHEMA)
    assert data["kind"] == "Environment"


def test_missing_manifest_raises(tmp_path: Path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(ManifestValidationError):
        load_manifest(missing, SCHEMA)


def test_invalid_manifest_field(tmp_path: Path):
        # invalid category value
        bad = tmp_path / "bad.yaml"
        bad.write_text(
                """
apiVersion: gateos.ultracube.v1alpha1
kind: Environment
metadata:
    name: badenv
spec:
    profile:
        category: not-valid
    containers:
        - name: c1
            image: example/image:latest
"""
        )
        with pytest.raises(ManifestValidationError):
                load_manifest(bad, SCHEMA)


def test_invalid_missing_required(tmp_path: Path):
        # missing containers
        bad = tmp_path / "bad2.yaml"
        bad.write_text(
                """
apiVersion: gateos.ultracube.v1alpha1
kind: Environment
metadata:
    name: badenv2
spec:
    profile:
        category: dev
"""
        )
        with pytest.raises(ManifestValidationError):
                load_manifest(bad, SCHEMA)
def test_security_capability_allowlist_invalid(tmp_path: Path):
        manifest = tmp_path / "sec.yaml"
        manifest.write_text(
                """
apiVersion: gateos.ultracube.v1alpha1
kind: Environment
metadata:
    name: secbad
spec:
    profile:
        category: security
    containers:
        - name: tool
            image: example/security:latest
            capabilities: [haxxor]
"""
        )
        with pytest.raises(ManifestValidationError):
                load_manifest(manifest, SCHEMA)


def test_security_capability_allowlist_valid(tmp_path: Path):
        manifest = tmp_path / "sec-ok.yaml"
        manifest.write_text(
                """
apiVersion: gateos.ultracube.v1alpha1
kind: Environment
metadata:
    name: secok
spec:
    profile:
        category: security
    containers:
        - name: tool
            image: example/security:latest
            capabilities: [netraw]
"""
        )
        data = load_manifest(manifest, SCHEMA)
        assert data["metadata"]["name"] == "secok"

