# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog and Semantic Versioning (will be adopted once < 1.0 stabilizes).

## [Unreleased]

### Added

- Graceful telemetry batch flush on process exit.
- Integration test for successful container switch path.
- Release automation script.
- Schema version negotiation (manifest `schemaVersion` support, v1.0 packaged schema).
- Plugin entry point discovery (group `gateos.plugins`) with opt-out env var.
- Security policy unit tests (capability allowlist) & plugin discovery tests.
- Schema version negotiation tests (valid/missing/unsupported cases).

### Changed

- Bumped version to 0.0.2 (pending tag).

### Planned

- Further container isolation (seccomp/AppArmor profiles).
- Graceful shutdown via API endpoint to trigger flush & plugin shutdown.

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
[0.0.2]: https://github.com/Ultra-Cube/Gate-OS/compare/v0.0.1...v0.0.2 (tag to be created)
[0.0.1]: https://github.com/Ultra-Cube/Gate-OS/releases/tag/v0.0.1 (tag to be created)
