"""Temporary script to write stub doc content."""
import os

BASE = "/home/pc/ucube/project/Gate-OS/docs"

files = {}

files["product/features.md"] = """\
---
title: Product & Feature Specifications
project: Gate-OS
owner: Ultra Cube Tech
status: Active
last-updated: 2026-03-06
---

# Product & Feature Specifications

> Gate-OS is the intelligent, multi-environment OS manager for Linux — enabling instant context switching between Gaming, Dev, Design, and Media workspaces on a single machine.

---

## Core Features (v1.2.0 Implemented)

### 1. Environment Switching
- Declarative YAML manifests define each environment's services, containers, profiles and security policies
- `gateos validate` — schema-validates manifests before apply
- `switch_environment()` pipeline: validate → pre-hooks → stop services → apply profile → start containers → post-hooks → emit telemetry
- Rollback on any failure: stops started containers, restores prior profile, restarts stopped services
- Switch latency target: < 3 s (P95)

### 2. Container Orchestration
- Podman-first runtime with Docker fallback detection via `shutil.which`
- Per-environment container specs: image, ports, env vars, volume mounts, command
- Top-level mounts applied to every container in an environment
- Dry-run mode for CI / environments without a container runtime
- State tracking: `running / stopped / unknown` per container

### 3. Systemd Service Management
- Start/stop required and optional systemd services per environment
- Required service failures abort the switch; optional failures log a warning
- `is_active()` polling for real-time status
- Dry-run auto-enabled when `systemctl` is not present (WSL, containers)

### 4. Hardware Performance Profiles
- CPU governor switching: `performance / powersave / ondemand`
- GPU power mode stubs for NVIDIA and AMD
- NIC priority: `tc qdisc` bandwidth shaping
- Profile restore on rollback

### 5. Security & Isolation
- Ed25519 manifest signing and verification (`gateos sign` / `gateos verify`)
- Keypair generation (`gateos gen-keypair`)
- Capability allowlist policy per environment
- seccomp / AppArmor profile stubs via `apply_isolation()`
- RBAC-ready API auth with bearer token (env or file source)
- Rate limiting (configurable per-IP)

### 6. OTA Update Mechanism
- `gateos check-update` — polls GitHub Releases API; compares semver
- `gateos apply-update` — dry-run (HEAD check) or real deb download
- `schedule_apply()` — systemd drop-in strategy (Strategy 1) with flag-file fallback (Strategy 2)
- Pre-release opt-in via `--include-prerelease`

### 7. Observability
- Structured JSON logs (stdout) for every switch event
- OTLP/HTTP JSON exporter — spans + logs + batch; configurable endpoint
- `@otlp_span()` decorator on `switch_environment()` pipeline
- Prometheus metrics registry: Counter, Gauge, Histogram
- `GATEOS_OTLP_DISABLE=1` kill-switch for air-gapped environments

### 8. REST + WebSocket Control API
- FastAPI server: `GET /environments`, `GET /environment/{name}`, `POST /switch`
- Bearer token auth; rate limiting at API boundary
- WebSocket endpoint for real-time switch status events
- OpenAPI schema auto-generated at `/docs`

### 9. Plugin System
- `pre_switch` / `post_switch` / `shutdown` hook points
- Entry-point discovery via `importlib.metadata`
- Invoke-all semantics; errors are logged but do not abort the switch

### 10. Mobile Companion
- WebSocket protocol: `SWITCH_ENV`, `STATUS_UPDATE`, `ERROR` message types
- JWT-signed payloads; PING/PONG keepalive
- Flutter client spec documented in `docs/mobile/companion-api.md`

---

## Feature Prioritization — MoSCoW

| Feature | Category | Priority | Status |
|---|---|---|---|
| Environment switch core | Core | **Must** | ✅ Done |
| Service + container orchestration | Core | **Must** | ✅ Done |
| Hardware profile (CPU governor) | Performance | **Must** | ✅ Done |
| Manifest signing (Ed25519) | Security | **Must** | ✅ Done |
| OTA update (check + apply) | Operations | **Must** | ✅ Done |
| REST + WebSocket API | Integration | **Should** | ✅ Done |
| Structured logging + OTLP traces | Observability | **Should** | ✅ Done |
| Plugin hooks | Extensibility | **Should** | ✅ Done |
| GPU profile (NVIDIA/AMD) | Performance | **Could** | ⏳ v1.3.0 |
| OIDC-backed API auth | Security | **Could** | ⏳ v1.3.0 |
| Plugin sandbox (subprocess) | Security | **Could** | ⏳ v1.3.0 |
| Cloud config sync | Productivity | **Won't** (v1) | 📋 Future |
| Windows/macOS port | Portability | **Won't** (v1) | 📋 Future |

---

## Acceptance Criteria

### Environment Switch
- **Given** a valid manifest, **When** `switch_environment("gaming")` is called, **Then** all defined services start, containers run, and telemetry event `switch.end` emits `status=success` within 3 s.
- **Given** a required service fails, **When** the switch runs, **Then** rollback triggers and `SwitchError` is raised.

### Manifest Validation
- **Given** a YAML file missing required field `name`, **When** `gateos validate` runs, **Then** exit code 1 and a `FAIL: <path>: ...` message is written to stderr.

### OTA Update
- **Given** a newer version exists on GitHub Releases, **When** `gateos check-update` runs, **Then** version + download URL are printed and exit code is 0.
- **Given** `--yes` is passed to `apply-update`, **When** the download succeeds, **Then** a `.ready` marker is written to `GATEOS_UPDATE_DIR`.

---

## Key Metrics

| Metric | Target | Current |
|---|---|---|
| Switch p95 latency | < 3 s | ~10 ms (dry-run) |
| Test coverage | ≥ 90% | **95%** |
| Test count | ≥ 200 | **308** |
| Cyclomatic complexity (per fn) | < 10 | ✅ Validated |

---

**Date:** March 2026 | **By:** Fadhel.SH
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/) | [LinkedIn](https://www.linkedin.com/company/ultra-cube)
"""

files["business/vision-mission.md"] = """\
---
title: Gate-OS Vision & Mission
project: Gate-OS
owner: Ultra Cube Tech
status: Active
last-updated: 2026-03-06
---

# Gate-OS Vision & Mission

---

## Vision

**Gate-OS is the universal, context-aware Linux platform for power users** — a single machine that becomes any environment you need, in seconds.

We envision a world where Linux users never have to choose between gaming performance, developer ergonomics, design workflows, and multimedia production on the same hardware. Gate-OS makes the machine adapt to the user — not the other way around.

---

## Mission

Ultra Cube Tech builds **modular, open, and trustworthy infrastructure software** that enables Linux power users and enterprises to:

1. Switch seamlessly between fully isolated computing environments — Gaming, Dev, Design, Media — with a single command or click.
2. Guarantee performance, security, and integrity across every switch through declarative manifests, hardware profiles, and cryptographic signing.
3. Observe and control every aspect of the platform via an open telemetry + API layer.

---

## Core Values

| Value | What It Means for Gate-OS |
|---|---|
| **Openness** | Apache 2.0 licensed; fully auditable; community contributions welcome |
| **Reliability** | Rollback on failure; P95 switch latency < 3 s; ≥ 95% test coverage |
| **Security** | Ed25519 manifest signing; capability allowlists; supply chain integrity |
| **Simplicity** | One YAML manifest per environment; one command to switch |
| **Observability** | Every action emits structured logs + OTLP spans; nothing is invisible |

---

## Strategic Pillars

### 1 — Unified Multi-Environment Experience
A single runtime manager that orchestrates services, containers, hardware profiles, and security policies as a single atomic operation.

### 2 — Performance & Reliability
Deterministic switching with automatic rollback, hardware-level profile tuning (CPU governor, GPU power mode, NIC priority), and benchmark-gated CI pipelines.

### 3 — Security & Trust (Enterprise-Ready)
Manifest signing verifies provenance. Plugin sandboxing prevents malicious extensions. API token rotation and OIDC integration (v1.3.0) enable enterprise deployment.

### 4 — Community-Driven Innovation
Open plugin architecture with entry-point discovery. Public roadmap and versioned milestones. Contributing guide and governance policy.

---

## Value Proposition

### For Linux Power Users
- Zero-friction context switching — no reboots, no profile juggling, no manual systemd service management.
- Confidence that gaming workloads won't bleed into dev workloads (separate containers, services, CPU policies).

### For Development Teams
- Reproducible environment definitions as code (YAML manifests, schema-validated).
- Consistent dev environments across all team machines — switch command is idempotent.

### For Enterprises
- Signed manifests provide audit trails for environment configurations.
- OTLP telemetry integrates with existing observability stacks (Grafana, Jaeger, OpenTelemetry Collector).
- REST API enables automated orchestration from CI/CD pipelines.

---

## Success Metrics

| Metric | Year 1 Target | Current (v1.2.0) |
|---|---|---|
| GitHub Stars | 500 | — |
| Active Monthly Users | 200 | Early adopters |
| Environment Switch Latency (P95) | < 3 s | ~10 ms (dry-run) |
| Test Coverage | ≥ 90% | **95%** |
| Community Contributors | 10 | 1 (founder) |
| Enterprise Pilots | 2 | 0 (pre-launch) |
| Plugin Ecosystem Size | 5 plugins | 0 (API stable) |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Fragmented tooling competition (Distrobox, toolbox) | Medium | Focus on full-stack orchestration; those tools manage containers only |
| Performance regression in real podman/docker switching | High | Benchmarks in CI; dry-run unit tests; latency gate |
| Security surface growth with plugin system | High | Signature verification + subprocess sandbox (v1.3.0) |
| Adoption friction (Linux-only, CLI-first) | Medium | MkDocs site, getting-started tutorial, mobile companion app |
| Upstream container runtime changes | Medium | Runtime abstraction (podman → docker fallback) |

---

**Date:** March 2026 | **By:** Fadhel.SH
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/) | [LinkedIn](https://www.linkedin.com/company/ultra-cube)
"""

files["security/threat-model.md"] = """\
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
| **Manifest Integrity** | Ed25519 signing (`gateos sign/verify`) ✅ | Policy engine enforcement (v1.3.0) |
| **Plugin Execution** | Entry-point discovery + `invoke()` | Signature verification + subprocess sandbox (v1.3.0) |
| **Container Images** | Image name in manifest; dry-run mode | Digest pin enforcement + warn on tag-only refs (v1.3.0) |
| **Telemetry Transport** | Plain HTTP OTLP (local collector) | TLS (`GATEOS_OTLP_TLS_CERT`), PII redaction (v1.3.0) |
| **WebSocket Auth** | Bearer token on connect (spec) | Enforce in server implementation (v1.3.0) |
| **Rate Limiting** | Per-IP sliding window ✅ | Configurable window via env vars |
| **Capability Policy** | `capability-policy.json` allowlist ✅ | Extend to container `--cap-drop` flags |

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
**Control:** Token read from `GATEOS_API_TOKEN` env var or file path `GATEOS_API_TOKEN_FILE`; not committed to config.
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
- [ ] SBOM attestation chain from CI → release artifact
- [ ] Network namespace isolation per container

---

**Date:** March 2026 | **By:** Fadhel.SH
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/)
"""

for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {rel_path} ({len(content.splitlines())} lines)")

print("All done.")
