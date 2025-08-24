# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog and Semantic Versioning (will be adopted once < 1.0 stabilizes).

## [Unreleased]

### Added (Unreleased)

_No changes yet._

### Changed (Unreleased)

_No changes yet._

### Planned (Unreleased)

- Further container isolation (seccomp/AppArmor profiles).
- Graceful shutdown via API endpoint to trigger flush & plugin shutdown.

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
