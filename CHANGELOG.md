# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) | Versioning: [Semantic Versioning](https://semver.org/)

---

## [Unreleased] — Target: 0.1.0

### Planned
- Real switch engine: systemd service orchestration + real podman/docker container start/stop.
- GTK4 UI shell (Adw.Application) with environment list and switch panel.
- Ubuntu 24.04 LTS ISO build script (`scripts/build-iso.sh`).
- ServiceManager class for managing systemd units per environment.
- Performance benchmark test (target: < 3s switch latency).
- AppArmor profile stubs per environment.
- Further container isolation (seccomp/AppArmor profiles).
- Graceful shutdown via API endpoint to trigger flush & plugin shutdown.

---

## [0.0.5] — 2026-03-05

### Added
- `TODO.md` — living task board with all work phases (Phase 0–9) and per-task status (✅/🔄/⏳/📋).
- `Makefile` — developer shortcuts: `make setup`, `make test`, `make test-cov`, `make lint`, `make lint-fix`, `make validate`, `make api`, `make token`, `make check`, `make clean`.
- `.gitignore` — covers Python pycache/eggs, venv, Node `package-lock.json`, Gate-OS runtime dirs, secrets.
- `gateos_manager/services/__init__.py` — `ServiceManager` class: start/stop systemd services from manifest `spec.services`, dry-run fallback when `systemctl` unavailable, required vs optional service distinction, `ServiceError` on critical failures, full telemetry events.
- `gateos_manager/profile/__init__.py` — `ProfileApplicator` class: applies CPU governor via sysfs, GPU mode stub, NIC priority stub, `restore_defaults()` for rollback; dry-run mode.
- `tests/test_service_manager.py` — 8 tests: dry-run start/stop, empty services, no-name skip, status, required failure raises, optional failure silent.
- `tests/test_profile_applicator.py` — 8 tests: CPU governor (valid/unknown), GPU stub, NIC stub, empty/absent performance key, all-settings, restore defaults.
- `tests/test_switch_orchestrator_enhanced.py` — 5 tests: SwitchContext defaults, correlation ID, perform_switch with services, missing manifest error.

### Changed
- `gateos_manager/switch/orchestrator.py` — full rewrite from stub to real pipeline: `SwitchContext` dataclass (tracks started containers/services/profile for rollback); activation steps (pre_switch → services → profile → containers → post_switch); `_rollback()` best-effort recovery; `ManifestValidationError` import removed (covered by base `Exception`).
- `pyproject.toml` — version bumped `0.0.4 → 0.0.5`; `httpx>=0.27.0` added to `[dev]` (required by FastAPI `TestClient`); description updated.
- `scripts/setup-dev-env.sh` — complete rewrite: fixed duplicated shebang/content, added apt auto-install fallback for Ubuntu, Python 3.10+ version validation, venv creation check, post-install test run for verification.
- `CONTRIBUTING.md` — `Getting Started` section replaced with full Ubuntu 24.04 prerequisites, `make` targets reference table.
- `docs/plan/project-plan.md` — Ubuntu 24.04 LTS base OS confirmed with rationale; 3-phase installable OS roadmap (Alpha May 2026, Beta Aug 2026, v1.0 Q4 2026); team adoption plan (Step 1–4); milestones M12–M17 added; risk register expanded.

### Fixed
- Missing `httpx` dependency caused `FastAPI TestClient` import failure in 3 test files (`test_api_server.py`, `test_auth.py`, `test_rate_limit.py`).
- `setup-dev-env.sh` had duplicated `#!/usr/bin/env bash` and conflicting logic.

### Test Results
- **64 tests passing** (up from 43 in v0.0.4)
- New tests: +21 (ServiceManager: 8, ProfileApplicator: 8, SwitchContext: 5)

## [0.0.4] - 2025-08-24

### Added (0.0.4)

- Telemetry batch size threshold test and stabilization of batching logic coverage.
- Multi-client rate limit isolation test.
- Additional negative security capability tests (multiple invalid caps mixed with valid).
- PyPI publish workflow using trusted publishing (OIDC) on tags `v*`.

### Changed (0.0.4)

- Control API now honors `x-client-id` header for per-client rate limiting
	(previously only query param / fallback caused bucket collision).
- Raised overall test count and coverage (43 passing tests) and stabilized telemetry batch size test timing.
- Version bumped to 0.0.4.

### Fixed (0.0.4)

- Rate limiting incorrectly aggregating different clients due to missing header extraction; now resolved.
- Flaky assertion in telemetry batch size test (timing variance) relaxed to acceptable range.

### Notes (0.0.4)

Quality hardening release prior to next feature expansion (isolation profiles &
API shutdown endpoint planned). Focus on correctness of rate limiting, telemetry
batching behavior, and publish pipeline readiness.

## [0.0.3] - 2025-08-24

### Added (0.0.3)

- Graceful telemetry batch flush on process exit.
- Integration test for successful container switch path.
- Release automation script.
- Schema version negotiation (manifest `schemaVersion` support, v1.0 packaged schema).
- Plugin entry point discovery (group `gateos.plugins`) with opt-out env var.
- Security policy unit tests (capability allowlist) & plugin discovery tests.
- Schema version negotiation tests (valid/missing/unsupported cases).

### Changed (0.0.3)

- Coverage threshold increased to 65%.
- Added manifest versioning & plugin discovery documentation.

### Notes (0.0.3)

Foundation hardening of extensibility (plugins) and governance around manifest evolution.

## [0.0.2] - 2025-08-24

### Added (Pre-release Enhancements)

- Expanded root README with comprehensive documentation index.
- CHANGELOG initialized.

### Notes

Documentation and scaffolding improvements ahead of first tag.

## [0.0.1] - 2025-08-24

### Added (Initial Release)

- Environment manifest loader & schema validation.
- Security capability allowlist enforcement.
- FastAPI Control API with token auth, rate limiting, correlation IDs, Pydantic models.
- Telemetry emitter (stdout/file + OTLP HTTP + optional batching) & structured JSON logging.
- Plugin registry with pre_switch, post_switch, shutdown hooks; sample plugin.
- ContainerManager with runtime detection (podman/docker) & dry-run mode, isolation stubs.
- Hot reload watcher (optional) for manifest directory.
- Tests for manifests, API, plugins, logging, containers, watch, failure shutdown hook.
- Documentation set (architecture, product, roadmap, security, contribution, UI/UX, API spec).

### Notes (Initial Release)

Early scaffold; API and module interfaces may change without deprecation.

[Unreleased]: https://github.com/Ultra-Cube/Gate-OS/compare/main...HEAD
[0.0.4]: https://github.com/Ultra-Cube/Gate-OS/compare/v0.0.3...v0.0.4 (tag to be created)
[0.0.3]: https://github.com/Ultra-Cube/Gate-OS/compare/v0.0.2...v0.0.3 (tag to be created)
[0.0.2]: https://github.com/Ultra-Cube/Gate-OS/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Ultra-Cube/Gate-OS/releases/tag/v0.0.1 (tag to be created)
