# Changelog

All notable changes to Gate-OS are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned (v1.3.0)
- Plugin sandboxing via subprocess isolation
- OIDC-backed API authentication
- Unsigned manifest rejection (`--require-sig` flag)
- Container image digest pin enforcement
- TLS OTLP transport (`GATEOS_OTLP_TLS_CERT`)
- GPU profile enforcement (NVIDIA driver API, ROCm)
- AppArmor profile generation from manifest

---

## [1.2.0] — 2026-03-06

### Added
- **Coverage Sprint**: test suite expanded from 228 to **308 tests** (87% → **95% coverage**)
- `test_container_manager_runtime.py` — 28 tests; `ContainerManager` coverage 50% → 99%
- `test_service_manager_runtime.py` — 25 tests; `ServiceManager` coverage 67% → 100%
- `test_cli_extended.py` — 35 tests; CLI coverage 73% → 96%
- `test_updater_extended.py` — 10 tests; Updater coverage 80% → 100%
- `@otlp_span("switch.pipeline")` decorator on `switch_environment()` in `orchestrator.py`
- `otlp_span()` context manager / decorator in `gateos_manager/telemetry/otlp.py`

### Changed
- Architecture diagrams updated with Mermaid C4, sequence, module boundary, and API flow diagrams
- `docs/architecture/overview.md` rewritten with real component descriptions
- `docs/roadmap/milestones.md` updated to reflect delivered milestones M1–M29

### Fixed
- Dry-run mode now correctly detected when `systemctl` is absent (WSL environments)
- OTLP batch export timeout configurable via `GATEOS_OTLP_TIMEOUT`

---

## [1.1.0] — 2025-12-15

### Added
- OTA update commands: `gateos check-update`, `gateos apply-update`
- `schedule_apply()` with systemd drop-in strategy and flag-file fallback
- Plugin system: entry-point discovery, `pre_switch`/`post_switch`/`shutdown` hooks
- WebSocket control API (`/ws` endpoint) with `SWITCH_ENV`, `STATUS_UPDATE`, `ERROR` messages
- Prometheus metrics registry: Counter, Gauge, Histogram
- Rate limiting on REST API (per-IP sliding window)
- `gateos plugins list` CLI command
- Mobile companion API documentation (`docs/mobile/companion-api.md`)

### Changed
- FastAPI server promoted from prototype to production-ready with bearer token auth
- Manifest YAML schema updated to `v1.0` (stable) — added `hooks` and `security_policy` sections

### Fixed
- Container rollback now correctly calls `stop` on containers started in the same switch
- Service manager `is_active()` now handles `systemctl` timeout gracefully

---

## [1.0.0] — 2025-09-01

### Added (initial release)
- Core environment switching pipeline: validate → pre-hooks → services → hardware → containers → post-hooks → telemetry
- YAML manifest support with JSON Schema validation
- Podman-first container runtime (Docker fallback)
- systemd service management (start/stop required/optional)
- Hardware profile: CPU governor, GPU power mode stub, NIC priority
- Ed25519 manifest signing: `gen-keypair`, `sign`, `verify`
- Capability allowlist security policy
- OTLP/HTTP JSON telemetry exporter
- FastAPI REST API: `GET /environments`, `GET /environment/{name}`, `POST /switch`
- CLI: `validate`, `list`, `switch`, `sign`, `verify`, `gen-keypair`, `api`
- Automatic rollback on switch failure
- AppArmor integration stubs (`apply_isolation()`)
- SBOM generation (Syft) and vulnerability scan (Grype) in CI
- MkDocs Material documentation site

---

## [0.1.0-beta] — 2025-07-01

### Added (beta)
- Project scaffolding: Python package, pyproject.toml, Makefile, pre-commit
- Initial manifest loader and schema stub
- Basic CLI skeleton
- CI/CD pipeline: pytest, ruff, flake8, coverage gate
- Architecture decision records (ADRs)
- Phase 0–3 milestones completed

---

[Unreleased]: https://github.com/Ultra-Cube/Gate-OS/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/Ultra-Cube/Gate-OS/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Ultra-Cube/Gate-OS/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/Ultra-Cube/Gate-OS/compare/v0.1.0-beta...v1.0.0
[0.1.0-beta]: https://github.com/Ultra-Cube/Gate-OS/releases/tag/v0.1.0-beta
