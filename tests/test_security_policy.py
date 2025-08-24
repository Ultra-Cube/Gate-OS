import pytest
from gateos_manager.security.policy import validate_security_manifest, SecurityPolicyError


def test_security_policy_valid_capabilities():
    manifest = {
        "kind": "Environment",
        "spec": {
            "profile": {"category": "security"},
            "containers": [
                {"name": "tool", "image": "x", "capabilities": ["netraw", "pcap"]}
            ],
        },
    }
    # Should not raise
    validate_security_manifest(manifest)


def test_security_policy_invalid_capabilities():
    manifest = {
        "kind": "Environment",
        "spec": {
            "profile": {"category": "security"},
            "containers": [
                {"name": "tool", "image": "x", "capabilities": ["rootfs", "pcap"]}
            ],
        },
    }
    with pytest.raises(SecurityPolicyError):
        validate_security_manifest(manifest)
