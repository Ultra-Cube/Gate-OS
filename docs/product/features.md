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
- \gateos validate\ — schema-validates manifests before apply
- \switch_environment()\ pipeline: validate → pre-hooks → stop services → apply profile → start containers → post-hooks → emit telemetry
- Rollback on any failure: stops started containers, restores prior profile, restarts stopped services
- Switch latency target: < 3 s (P95 at 95th percentile)

### 2. Container Orchestration
- Podman-first runtime with Docker fallback detection via \shutil.which\
- Per-environment container specs: image, ports, env vars, volume mounts, command
- Top-level mounts applied to every container in an environment
- Dry-run mode for CI / environments without a container runtime
- State tracking: \unning / stopped / unknown\ per container

### 3. Systemd Service Management
- Start/stop required and optional systemd services per environment
- Required service failures abort the switch; optional failures log a warning
- \is_active()\ polling for real-time status
- Dry-run auto-enabled when \systemctl\ is not present (WSL, containers)

### 4. Hardware Performance Profiles
- CPU governor switching: \performance / powersave / ondemand\
- GPU power mode stubs for NVIDIA and AMD
- NIC priority: \	c qdisc\ bandwidth shaping
- Profile restore on rollback

### 5. Security & Isolation
- Ed25519 manifest signing and verification (\gateos sign\ / \gateos verify\)
- Keypair generation (\gateos gen-keypair\)
- Capability allowlist policy per environment
- seccomp / AppArmor profile stubs via \pply_isolation()\
- RBAC-ready API auth with bearer token (env or file source)
- Rate limiting (configurable per-IP)

### 6. OTA Update Mechanism
- \gateos check-update\ — polls GitHub Releases API; compares semver
- \gateos apply-update\ — dry-run (HEAD check) or real deb download
- \schedule_apply()\ — systemd drop-in strategy (Strategy 1) with flag-file fallback (Strategy 2)
- Pre-release opt-in via \--include-prerelease\

### 7. Observability
- Structured JSON logs (stdout) for every switch event
- OTLP/HTTP JSON exporter — spans + logs + batch; configurable endpoint
- \@otlp_span()\ decorator on \switch_environment()\ pipeline
- Prometheus metrics registry: Counter, Gauge, Histogram
- \GATEOS_OTLP_DISABLE=1\ kill-switch for air-gapped environments

### 8. REST + WebSocket Control API
- FastAPI server: \GET /environments\, \GET /environment/{name}\, \POST /switch\
- Bearer token auth; rate limiting at API boundary
- WebSocket endpoint for real-time switch status events
- OpenAPI schema auto-generated at \/docs\

### 9. Plugin System
- \pre_switch\ / \post_switch\ / \shutdown\ hook points
- Entry-point discovery via \importlib.metadata\
- Invoke-all semantics; errors are logged but do not abort the switch

### 10. Mobile Companion
- WebSocket protocol: \SWITCH_ENV\, \STATUS_UPDATE\, \ERROR\ message types
- JWT-signed payloads; PING/PONG keepalive
- Flutter client spec documented in \docs/mobile/companion-api.md\

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
- **Given** a valid manifest, **When** \switch_environment(\
