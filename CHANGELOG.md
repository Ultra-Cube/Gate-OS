# Changelog

All notable changes to this project will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) | Versioning: [Semantic Versioning](https://semver.org/)

---

## [Unreleased] — Target: 1.0.0-beta

### Planned
- All 4 core environments validated end-to-end.
- OTA update mechanism stub.
- Beta release notes and migration guide.

---

## [0.5.0] — 2026-03-05 — Mobile Companion API

### Added
- `gateos_manager/api/websocket.py` — WebSocket real-time status endpoint:
  - `ConnectionManager` — thread-safe multi-client broadcast pool with dead-connection cleanup.
  - `GET /ws/status` WebSocket endpoint — sends welcome on connect, echoes pings.
  - `broadcast_sync()` — fire-and-forget from synchronous code; tasks broadcast on live loop.
  - `_make_message()` helper — consistent JSON message envelope with ISO-8601 timestamp.
- `POST /switch/{env}` — now broadcasts `switch_done` message to all WebSocket clients after every successful switch.
- `GET /ws/status` route registered in FastAPI app via `app.include_router(ws_router)`.
- `docs/mobile/companion-api.md` — comprehensive mobile companion documentation:
  - WebSocket message type reference table.
  - REST remote switch usage.
  - Flutter scaffold setup guide.
  - Security considerations (TLS, Keystore).
  - Roadmap table v0.5.0 → v1.0.0.
- `tests/test_mobile_companion.py` — 12 tests covering ConnectionManager, message helpers, WebSocket endpoint, anyio-based async tests.

### Fixed
- `gateos_manager/telemetry/emitter.py` — `_flush_loop` now re-reads `GATEOS_TELEMETRY_BATCH_INTERVAL` and `GATEOS_TELEMETRY_BATCH_SIZE` each cycle (was captured once at thread start), fixing a timing flakiness in tests.

---

## [0.4.0] — 2026-03-05 — Performance & Observability

### Added
- `gateos_manager/telemetry/prometheus.py` — in-process Prometheus metrics:
  - `Counter`, `Gauge`, `Histogram` primitives (thread-safe, zero dependencies).
  - `MetricsRegistry` with pre-declared metrics: `gateos_switch_total`, `gateos_switch_latency_seconds`, `gateos_switch_latency_p99_seconds`, `gateos_active_environment`, `gateos_api_requests_total`, `gateos_memory_delta_bytes`, `gateos_build_info`.
  - `start_metrics_server(port)` — daemon HTTP server on `/metrics` (Prometheus text format 0.0.4).
  - P99 rolling window (last 100 samples) without external libraries.
- `GET /metrics` FastAPI endpoint — returns Prometheus text exposition from `registry`.
- HTTP middleware on all API routes — auto-increments `gateos_api_requests_total` with method/path/status labels.
- `POST /switch/{name}` — increments `gateos_switch_total` with env and status labels on every switch.
- `tests/test_observability.py` — 19 tests:
  - Counter/Gauge/Histogram unit tests.
  - Registry text format assertions.
  - FastAPI `/metrics` endpoint integration tests.
  - Perf CI gate: switch pipeline must complete in < 3 s (marked `benchmark`).
  - Metrics server start/stop/404 tests.

---

## [0.3.0] — 2026-03-05 — Security Hardening

### Added
- `profiles/apparmor/` — AppArmor profiles for all five environments:
  - `gateos-env-dev` — deny-list; allows git, Python, Node, Cargo, Go, Podman.
  - `gateos-env-gaming` — GPU devices, Steam/Proton/Wine/Lutris, `sys_nice`.
  - `gateos-env-security` — strict isolation, raw sockets (nmap/tshark), no GPU, audited denies.
  - `gateos-env-design` — GIMP, Inkscape, Blender, GPU for rendering.
  - `gateos-env-media` — VLC, OBS, Ardour, video capture devices, `sys_nice`.
- `profiles/seccomp/gateos-default.json` — OCI seccomp allowlist for all container environments.
- `profiles/seccomp/gateos-security.json` — strict seccomp for security environment; blocks `init_module`, `kexec_load`, `mount`, `unshare`, `setns`, privilege escalation paths.
- `gateos_manager/security/signing.py` — Ed25519 manifest signing module:
  - `sign(manifest_path)` — signs manifest and writes `.sig` file.
  - `verify(manifest_path, sig_path)` — verifies Ed25519 signature.
  - `generate_keypair(key_dir)` — generates PEM keypair for dev/key-rotation.
- CLI subcommands: `gateos sign`, `gateos verify`, `gateos gen-keypair`.
- `tests/test_security_hardening.py` — 33 tests covering AppArmor syntax, seccomp schema, signing round-trip, tamper detection, and CLI integration.

### Fixed
- `pyproject.toml` — removed duplicate `[project.optional-dependencies.ui]` section.

---

## [0.2.0] — 2026-03-05 — Ubuntu ISO Builder

### Added
- `scripts/build-iso.sh` — full automated Ubuntu 24.04 LTS ISO build script:
  - Downloads Ubuntu 24.04 base ISO (cached in CI), extracts squashfs.
  - Chroot customization: installs gateos-manager, PyGObject, podman, desktop file.
  - Repacks squashfs with xz compression, applies Gate-OS GRUB branding.
  - Builds final hybrid ISO (BIOS + UEFI) with xorriso; generates SHA-256 checksum.
  - Supports `--dry-run`, `--skip-download`, `--version`, `--output` flags.
- `data/systemd/gateos-api.service` — production systemd unit with security hardening:
  - `ProtectSystem=strict`, `PrivateTmp`, `NoNewPrivileges`, `RestrictNamespaces`.
  - Auto-generates API token on first start via `ExecStartPre`.
  - Restart policy: `on-failure`, max 3 retries per 60 s.
- `gateos_manager/packaging/__init__.py` — Python packaging utilities:
  - `build_deb()` — generates `.deb` package (DEBIAN/control, postinst, prerm, install tree).
  - `generate_preseed()` — Ubuntu auto-install preseed config stub.
  - `generate_postinstall_script()` — standalone overlay install script.
- `docs/installation/guide.md` — full installation guide:
  - ISO flashing with Ventoy / `dd` / Rufus.
  - Overlay install on existing Ubuntu 24.04.
  - Post-install configuration, API token setup, environment switching.
  - Troubleshooting table for common issues.
- `.github/workflows/build-iso.yml` — CI workflow that builds and publishes ISO on release tags.
- `tests/test_packaging.py` — **14 new tests** for packaging utilities (all dry-run safe).

### Changed
- `gateos_manager/__init__.py` — version bumped to `0.2.0`; `packaging` added to `__all__`.
- `pyproject.toml` — version `0.1.0 → 0.2.0`; updated description.
- `[tool.hatch.build]` — includes `data/systemd/*.service`.

### Tests
- **114 tests passing** (was 100; +14 packaging tests)



## [0.1.0] — 2026-03-05 — GTK4 UI Shell

### Added
- `gateos_manager/ui/` package — full GTK4/Libadwaita UI shell:
  - `__init__.py` — `GTK_AVAILABLE` flag, `require_gtk()` guard, `GtkNotAvailableError`,
    `APP_ID`, `API_URL` constants. Graceful degradation when PyGObject not installed.
  - `api_client.py` — `GateOSAPI` synchronous HTTP client (stdlib `urllib`, no extra deps)
    wrapping `/environments`, `/switch/{name}`, `/health` endpoints with bearer token auth.
  - `env_list.py` — `EnvListPanel(Adw.PreferencesGroup)` + `EnvRow(Adw.ActionRow)` widgets;
    fetches environments from Control API, emits `env-selected` signal on switch request.
  - `switch_button.py` — `SwitchButton` compound widget with animated `Gtk.Spinner`
    during switch, success/failure badge, `switch-started/done/failed` signals.
  - `status_bar.py` — `StatusBar(Gtk.ActionBar)` with active-env label, live API health
    indicator (auto-polls every 5 s), and version badge.
  - `tray.py` — `AppIndicatorTray` system tray icon (AyatanaAppIndicator3); gracefully
    disabled when the library is absent.
  - `app.py` — `GateOSApp(Adw.Application)` + `GateOSWindow(Adw.ApplicationWindow)`;
    `GATEOS_UI_NO_DISPLAY=1` env var for headless/CI mode; `main()` entry point.
- `data/gate-os-manager.desktop` — XDG desktop entry for autostart and app launchers.
- `tests/test_ui_components.py` — **32 new tests** covering API client, env list,
  switch button, status bar, tray (all headless with full GTK mock — runnable in CI).
- `[project.scripts]` `gateos-ui` entry point in `pyproject.toml`.
- `[project.optional-dependencies]` `ui = ["PyGObject>=3.44.0"]` extra group.
- `[tool.hatch.build]` now includes `data/*.desktop`.

### Changed
- `gateos_manager/__init__.py` — added `__version__ = "0.1.0"` and exposed `ui` in `__all__`.
- `pyproject.toml` — version bumped `0.0.6 → 0.1.0`; updated description.

### Tests
- **100 tests passing** (was 68; +32 UI component tests)



## [0.0.6] — 2026-03-05

### Added
- `tests/test_perf_switch_latency.py` — 4 benchmark tests (`@pytest.mark.benchmark`):
  1-container, 3-container, 10-container, and 10× repeated-switch stability runs.
  All complete well under the 3 s SLA in dry-run mode (typically < 50 ms).
- `pyproject.toml` `[tool.pytest.ini_options]` — registered `benchmark` marker to suppress
  `PytestUnknownMarkWarning`; added default `addopts = "--tb=short"`.

### Changed
- `gateos_manager/containers/manager.py` — production-grade improvements:
  - Module-level `_START_TIMEOUT` (default 30 s) and `_STOP_TIMEOUT` (default 15 s) constants,
    overridable via `GATEOS_CONTAINER_START_TIMEOUT` / `GATEOS_CONTAINER_STOP_TIMEOUT` env vars.
  - `_start_single()` now captures stderr, checks `returncode`, and emits `status=error`
    on non-zero exit instead of silently succeeding.
  - `subprocess.TimeoutExpired` handled separately with a `status=timeout` telemetry event.
  - Container labelling: `--label gateos.env=<manifest_name>` and
    `--label gateos.managed=true` added to every `podman run` call.
  - Top-level `manifest.mounts` applied to every container via `-v source:target[:ro]`.
  - Per-container `spec.mounts` extends top-level mounts using the same `-v` syntax.
  - `_stop_single()` uses `podman rm --force` (was plain `rm`) so cleanup always succeeds
    even when the container has already exited; stop timeout applied here too.
  - `_start_single()` signature extended with `manifest_name` and `top_mounts` keyword args;
    `start()` passes these through.
  - Clarified docstring: added manifest contract example with `mounts` field + timeout docs.
- `pyproject.toml` — version bumped `0.0.5 → 0.0.6`.

### Fixed
- `_stop_single()` could silently leave orphaned containers if `podman rm` hit a non-zero exit
  (e.g. container already removed). Now uses `--force` flag to guarantee cleanup.
- Unchecked `subprocess.run` return codes in `_start_single()` could mark a failed container
  launch as `running`. Fixed by checking `result.returncode`.

### Test Results
- **68 tests passing** (up from 64 in v0.0.5)
- New tests: +4 (performance benchmarks)

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
