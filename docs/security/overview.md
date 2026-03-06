# Security Overview

Gate-OS applies a **layered security model** across manifests, API access, containers, plugins, and hardware profiles.

---

## Security Layers

```
Request (CLI / REST API)
       │
       ▼
  [1] API Authentication (Bearer Token)
       │
       ▼
  [2] Rate Limiting (per-IP sliding window)
       │
       ▼
  [3] Manifest Validation (JSON Schema)
       │
       ▼
  [4] Manifest Signing Verification (Ed25519)  ← v1.3.0: enforce-only mode
       │
       ▼
  [5] Security Policy Apply (isolation level, capability allowlist)
       │
       ▼
  [6] Container & Service Execution
       │
       ▼
  [7] Plugin Invocation (currently in-process; sandboxed in v1.3.0)
```

---

## Quick Reference

| Feature | Status | Detail |
|---|---|---|
| Bearer token auth | Done | `GATEOS_API_TOKEN` env var or file |
| Rate limiting | Done | Per-IP; configurable via `GATEOS_API_RATE_LIMIT` |
| Manifest schema validation | Done | `gateos validate` |
| Ed25519 manifest signing | Done | `gateos sign/verify/gen-keypair` |
| Capability allowlist | Done | `capability-policy.json` per env |
| AppArmor profiles | Partial | Profile stubs; enforcement in v1.3.0 |
| Plugin sandboxing | Planned | subprocess isolation (v1.3.0) |
| OIDC API auth | Planned | v1.3.0 |
| Unsigned manifest rejection | Planned | `--require-sig` flag (v1.3.0) |

---

## Detailed Guides

- [Manifest Signing](signing.md) — Ed25519 keys, sign/verify workflow
- [AppArmor Profiles](apparmor.md) — capability allowlist and isolation levels
- [Threat Model](threat-model.md) — attack surfaces, threat scenarios, open items
- [Supply Chain](../architecture/supply-chain.md) — SBOM, Grype, pip-audit

---

## API Security

The Gate-OS REST API requires a bearer token on every request:

```http
Authorization: Bearer <GATEOS_API_TOKEN>
```

Token is read from `GATEOS_API_TOKEN` (env var) or `GATEOS_API_TOKEN_FILE` (path to file). Neither source commits the token to configuration files.

Generate a token:
```bash
export GATEOS_API_TOKEN="$(openssl rand -hex 32)"
```

Rate limiting blocks more than `GATEOS_API_RATE_LIMIT` (default: 60) requests per minute per IP address.

---

## Manifest Security

### Validation
Every manifest is validated against the JSON Schema before any switch operation:

```bash
gateos validate environments/gaming.yaml
# OK: environments/gaming.yaml
```

### Signing (Recommended)
Sign manifests to guarantee they were not tampered with:

```bash
gateos gen-keypair --key-dir /etc/gateos/keys
gateos sign environments/gaming.yaml --key-dir /etc/gateos/keys
gateos verify environments/gaming.yaml --key-dir /etc/gateos/keys
# OK: signature valid
```

See [Signing](signing.md) for the complete workflow.

---

## Reporting Security Issues

Please report security vulnerabilities privately via GitHub Security Advisories:
[https://github.com/Ultra-Cube/Gate-OS/security/advisories](https://github.com/Ultra-Cube/Gate-OS/security/advisories)

Do **not** open public issues for security vulnerabilities.

---

## See Also
- [Signing](signing.md)
- [AppArmor](apparmor.md)
- [Threat Model](threat-model.md)
