# Changelog

All notable changes to this project will be documented in this file.

The format loosely follows Keep a Changelog and Semantic Versioning (will be adopted once < 1.0 stabilizes).

## [Unreleased]

### Added (Initial Release)

- Expanded root README with comprehensive documentation index.
- CHANGELOG initialized.

### Planned

- Versioned releases once core switch orchestration is feature-complete.

## [0.0.1] - 2025-08-24

### Added

- Environment manifest loader & schema validation.
- Security capability allowlist enforcement.
- FastAPI Control API with token auth, rate limiting, correlation IDs, Pydantic models.
- Telemetry emitter (stdout/file + OTLP HTTP + optional batching) & structured JSON logging.
- Plugin registry with pre_switch, post_switch, shutdown hooks; sample plugin.
- ContainerManager with runtime detection (podman/docker) & dry-run mode, isolation stubs.
- Hot reload watcher (optional) for manifest directory.
- Tests for manifests, API, plugins, logging, containers, watch, failure shutdown hook.
- Documentation set (architecture, product, roadmap, security, contribution, UI/UX, API spec).

### Notes

Early scaffold; API and module interfaces may change without deprecation.

[Unreleased]: https://github.com/Ultra-Cube/Gate-OS/compare/main...HEAD
[0.0.1]: https://github.com/Ultra-Cube/Gate-OS/releases/tag/v0.0.1 (tag to be created)
