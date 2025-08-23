# Capability Policy (Draft)

Gate-OS applies additional security validation for environments in the `security` category.

## Current Behavior (v0)

- Hardcoded allowlist enforced in `gateos_manager.security.policy.ALLOWED_SECURITY_CAPABILITIES`.
- Any container declaring a capability outside this set causes manifest validation failure.

Allowlist (initial):

- `netraw`
- `pcap`
- `lowlevel` (placeholder label – may be refined)

## Schema Notes

- `spec.containers[].capabilities` is a free-form string array but validated by policy when category = `security`.
- `spec.security.capabilityPolicy.allowlistRef` (new, future) will allow referencing named allowlists instead of hardcoding.

## Roadmap

| Phase | Change |
|-------|--------|
| v0 | Hardcoded Python set + validation hook |
| v1 | Named allowlist references in manifest (allowlistRef) |
| v2 | Dynamic policy bundles signed & loaded at runtime |
| v3 | Per-capability telemetry & usage audit |

## Planned Additional Controls

- Network namespace segmentation per container.
- Mandatory read-only root with ephemeral write layer.
- Automatic capability reduction after tool initialization.

---
**Date:** Aug 2025 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech

