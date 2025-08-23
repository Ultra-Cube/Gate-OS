"""Security policy stubs for Gate-OS environments.

Currently minimal; future expansion will enforce capability allowlists,
network isolation, and privilege constraints.
"""
from __future__ import annotations

from typing import Any

ALLOWED_SECURITY_CAPABILITIES = {
    # netraw kept for certain diagnostic tools; may tighten later
    "netraw",
    "pcap",
    "lowlevel",  # placeholder future label
}


class SecurityPolicyError(Exception):
    """Raised when a manifest violates security policy."""


def validate_security_manifest(manifest: dict[str, Any]) -> None:
    """Validate security-specific constraints.

    For category 'security' ensure declared container capabilities are from
    an allowlist.
    """
    if manifest.get("spec", {}).get("profile", {}).get("category") != "security":
        return
    containers = manifest.get("spec", {}).get("containers", [])
    for c in containers:
        caps = c.get("capabilities", []) or []
        invalid = [cap for cap in caps if cap not in ALLOWED_SECURITY_CAPABILITIES]
        if invalid:
            raise SecurityPolicyError(f"Invalid security capabilities: {invalid}")