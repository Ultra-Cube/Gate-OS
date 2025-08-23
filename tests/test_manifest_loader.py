from pathlib import Path
import pytest

from gateos_manager.manifest.loader import load_manifest, ManifestValidationError


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
