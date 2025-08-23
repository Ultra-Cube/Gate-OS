# Security Environment (Kali Toolset)

The security environment provides a curated offensive / diagnostic toolkit while preserving system safety.

## Goals

- Consolidate frequently used pentest tools (nmap, nikto, metasploit, Burp) in isolated containers.
- Enforce a conservative capability allowlist (initial: `netraw`, `pcap`, `lowlevel` placeholder).
- Maintain strict isolationLevel defaults.

## Manifest Example

See `examples/environments/security.yaml`.

## Policy

Validated in loader via `validate_security_manifest` (rejects non-allowlisted capabilities).

See also: `docs/security/capability-policy.md` for roadmap and details.

## Future Hardening

- Network namespace segmentation per container.
- Read-only root + ephemeral overlay.
- Audit log export to telemetry pipeline.

---
**Date:** Aug 2025 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
