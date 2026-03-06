# Threat Model

> **Status:** Active — last reviewed March 2026 (v1.2.0)

---

## Assets

| Asset | Confidentiality | Integrity | Availability |
|---|---|---|---|
| Environment manifests | Low | **Critical** | High |
| API tokens | **Critical** | High | Medium |
| Container images / digests | Low | **Critical** | High |
| Telemetry data | Medium | Medium | Low |
| Hardware profile state | Low | High | Medium |
| Plugin code | Low | **Critical** | Medium |

---

## Adversary Profiles

| Adversary | Access Level | Goal |
|---|---|---|
| Local unprivileged user | Shell access, no root | Escalate privileges via manifest injection or plugin |
| Malicious plugin author | Publishes entry-point package | Execute arbitrary code during environment switch |
| Supply chain attacker | Compromises PyPI / container registry | Inject malware via dependency or container image |
| Network attacker (MITM) | Local network | Intercept unencrypted OTLP traffic or API tokens |

---

## Attack Surfaces & Current Controls

| Surface | Current Control (v1.2.0) | Planned Control |
|---|---|---|
| **API Token** | Random 32-byte alphanumeric; env/file source | Token rotation endpoint (v1.3.0); OIDC (v1.3.0) |
| **Manifest Integrity** | Ed25519 signing (`gateos sign/verify`) done | Policy engine enforcement (v1.3.0) |
| **Plugin Execution** | Entry-point discovery + `invoke()` | Signature verification + subprocess sandbox (v1.3.0) |
| **Container Images** | Image name in manifest; dry-run mode | Digest pin enforcement + warn on tag-only refs (v1.3.0) |
| **Telemetry Transport** | Plain HTTP OTLP (local collector) | TLS (`GATEOS_OTLP_TLS_CERT`), PII redaction (v1.3.0) |
| **WebSocket Auth** | Bearer token on connect (spec) | Enforce in server implementation (v1.3.0) |
| **Rate Limiting** | Per-IP sliding window (done) | Configurable window via env vars |
| **Capability Policy** | `capability-policy.json` allowlist (done) | Extend to container `--cap-drop` flags |

---

## Threat Scenarios

### T1 — Manifest Injection
**Scenario:** Attacker writes a crafted manifest that triggers container start with a malicious image.  
**Control:** `gateos validate` schema-validates before switch; `gateos verify` checks Ed25519 signature.  
**Residual Risk:** Unsigned manifests accepted without `--require-sig` flag (planned v1.3.0).

### T2 — Malicious Plugin
**Scenario:** A pip package registers a `gateos.plugins` entry-point that executes shell commands in `pre_switch`.  
**Control:** None currently; plugins run in-process.  
**Planned:** Signature verification before load; subprocess sandbox with restricted capabilities (v1.3.0).

### T3 — API Token Exposure
**Scenario:** Token written to plaintext file; attacker reads it and calls `POST /switch`.  
**Control:** Token read from `GATEOS_API_TOKEN` env var or file path `GATEOS_API_TOKEN_FILE`; not committed.  
**Planned:** Token rotation endpoint; short-lived JWT option.

### T4 — Supply Chain (PyPI)
**Scenario:** Transitive dependency is compromised and injected with malicious code.  
**Control:** `pip-audit` in CI; pinned `requirements.txt`.  
**Planned:** SLSA provenance attestation on Gate-OS release artifacts.

### T5 — Container Image Tag Drift
**Scenario:** `redis:latest` points to a different image with CVEs between switches.  
**Control:** None currently; image name is taken from manifest.  
**Planned:** Warn when manifest image lacks `@sha256:` digest pin (v1.3.0).

---

## Open Items

- [ ] Encrypted at-rest persistent state (if any state is written to disk)
- [ ] Secure secret injection into containers (not via env vars in manifest plain text)
- [ ] SBOM attestation chain from CI to release artifact
- [ ] Network namespace isolation per container

---

**Date:** March 2026 | **By:** Fadhel.SH  
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/)
