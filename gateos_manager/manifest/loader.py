"""Environment manifest loading & validation (draft)."""
from __future__ import annotations

import importlib.resources as pkg_resources
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from gateos_manager.security import validate_security_manifest


@dataclass
class ManifestValidationError(Exception):
    message: str
    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


SUPPORTED_SCHEMA_VERSIONS = ["1.0"]  # extend as new versions added


def _resolve_schema(version: str | None, explicit_path: Path) -> Path:
    """Resolve schema path by version.

    Order:
      1. If explicit_path exists, use it.
      2. If version provided & packaged schema exists under resources, load it.
      3. Fallback: explicit_path (error if missing).
    """
    if explicit_path.exists():
        return explicit_path
    if version:
        if version not in SUPPORTED_SCHEMA_VERSIONS:
            raise ManifestValidationError(f"Unsupported manifest schemaVersion '{version}' (supported: {SUPPORTED_SCHEMA_VERSIONS})")
        # Attempt to load packaged schema (gateos_manager.manifest.schemas.environment-manifest-v{version}.yaml)
        resource_name = f"environment-manifest-v{version}.yaml"
        try:  # pragma: no cover - packaging dependent
            data = pkg_resources.files(__package__).joinpath("schemas").joinpath(resource_name)
            if data.is_file():
                return Path(str(data))
        except Exception:  # pragma: no cover
            pass
    # Last resort: raise if path not found
    raise ManifestValidationError(f"Schema not found: {explicit_path}")


def load_manifest(path: Path, schema_path: Path) -> dict[str, Any]:
    """Load and validate a manifest against a schema (with version negotiation).

    The manifest may declare `schemaVersion` at top-level or under `environment.schemaVersion`.
    If present we attempt to map to an internal packaged schema; otherwise the provided
    schema_path is used.
    """
    if not path.exists():  # noqa: SIM108 clarity
        raise ManifestValidationError(f"Manifest not found: {path}")

    try:
        # Support multi-document YAML (use first document) for flexibility
        data_docs = list(yaml.safe_load_all(path.read_text()))
        data = (data_docs[0] if data_docs else {}) or {}


        # Determine declared schema version (top-level or nested)
        declared_version = data.get("schemaVersion") or data.get("environment", {}).get("schemaVersion")
        if declared_version and declared_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise ManifestValidationError(f"Unsupported manifest schemaVersion '{declared_version}' (supported: {SUPPORTED_SCHEMA_VERSIONS})")

        # Resolve schema path (may raise if unsupported / missing)
        resolved_schema_path = (
            _resolve_schema(declared_version, schema_path)
            if declared_version
            else (schema_path if schema_path.exists() else schema_path)
        )

        schema_docs = list(yaml.safe_load_all(resolved_schema_path.read_text()))
        schema = (schema_docs[0] if schema_docs else {}) or {}

        jsonschema.validate(data, schema)

        # Security policy pass (wrap to unify error type)
        try:
            validate_security_manifest(data)
        except Exception as e:  # pragma: no cover - ensures error path caught upstream
            raise ManifestValidationError(str(e)) from e

        return data
    except jsonschema.ValidationError as e:  # pragma: no cover - formatting
        raise ManifestValidationError(f"schema validation error: {e.message}") from e
    except yaml.YAMLError as e:  # pragma: no cover
        raise ManifestValidationError(f"YAML parse error: {e}") from e
