"""Environment manifest loading & validation (draft)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
from gateos_manager.security import validate_security_manifest
import yaml


@dataclass
class ManifestValidationError(Exception):
    message: str
    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def load_manifest(path: Path, schema_path: Path) -> dict[str, Any]:
    """Load and validate a manifest against the schema.

    Parameters
    ----------
    path: Path to manifest YAML
    schema_path: Path to schema YAML
    Raises ManifestValidationError on validation fail.
    Returns manifest dict.
    """
    if not path.exists():  # noqa: SIM108 clarity
        raise ManifestValidationError(f"Manifest not found: {path}")
    if not schema_path.exists():
        raise ManifestValidationError(f"Schema not found: {schema_path}")
    try:
        # Support multi-document YAML (use first document) for flexibility
        data_docs = list(yaml.safe_load_all(path.read_text()))
        data = (data_docs[0] if data_docs else {}) or {}
        schema_docs = list(yaml.safe_load_all(schema_path.read_text()))
        schema = (schema_docs[0] if schema_docs else {}) or {}
        jsonschema.validate(data, schema)
        # Security policy pass
        try:
            validate_security_manifest(data)
        except Exception as e:  # pragma: no cover - ensures error path caught upstream
            raise ManifestValidationError(str(e)) from e
        return data
    except jsonschema.ValidationError as e:  # pragma: no cover - formatting
        raise ManifestValidationError(f"schema validation error: {e.message}") from e
    except yaml.YAMLError as e:  # pragma: no cover
        raise ManifestValidationError(f"YAML parse error: {e}") from e
