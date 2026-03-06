# Gate-OS — Task Board & Work Plan

> Living document — updated after every completed phase.  
> Last updated: **March 5, 2026**  
> Current version: **v1.1.0** → Next target: **v1.2.0** (Coverage Sprint & Docs)

| Symbol | Meaning |
|--------|---------|
| ✅ | Done & committed |
| 🔄 | In progress |
| ⏳ | Planned — next sprint |
| 📋 | Planned — future sprint |
| 🔴 | Blocked |
| ❌ | Cancelled |

---

## 🏁 Phase 0 — Foundation (v0.0.1 → v0.0.4) ✅ COMPLETE

All items committed and tagged.

- ✅ Project structure & Python package scaffold (`gateos_manager`)
- ✅ Environment manifest JSON Schema (v0.1.0) + examples (dev, gaming, design, media, security)
- ✅ Manifest loader & validator (`loader.py` + `jsonschema`)
- ✅ Schema version negotiation (schemaVersion field + packaged schema v1.0)
- ✅ Switch orchestrator skeleton (`switch/orchestrator.py`)
- ✅ Container manager (dry-run + podman/docker detection)
- ✅ Telemetry emitter (stdout JSON + OTLP batch queue)
- ✅ Structured logging (`logging/structured.py`)
- ✅ Plugin registry (entry points: `pre_switch`, `post_switch`, `shutdown`)
- ✅ FastAPI Control API (`/environments`, `/switch/{name}`) + token auth + rate limiting
- ✅ Security policy: capability allowlist for `security` category
- ✅ Security isolation stubs (`isolation.py`)
- ✅ Watch/reload daemon (`watch/reloader.py`)
- ✅ CLI: `gateos validate` / `gateos api` / `gateos gen-token`
- ✅ 43 passing tests (manifest, switch, security, containers, telemetry, API)
- ✅ CI: SBOM (Syft) + vulnerability scan (Grype)
- ✅ Scripts: `setup-dev-env.sh`, `dev-check.sh`, `release.sh`, `validate-manifests.sh`, `install-dde.sh`
- ✅ Docs: architecture, security, roadmap, API, environments, contribution

---

## 🔧 Phase 1 — Dev Environment Fix (v0.0.5) ✅ COMPLETE

**Goal:** Every team member can clone the repo and run tests in under 5 minutes.  
**Completed:** March 5, 2026

- ✅ Audit dev environment (pip/pytest not installed in base system)
- ✅ Update `docs/plan/project-plan.md` with full Ubuntu ISO roadmap
- ✅ Add `.gitignore` (Python, venv, Node, secrets)
- ✅ Fix `setup-dev-env.sh` (removed duplicated content, added apt auto-install, Python version check)
- ✅ Update `CONTRIBUTING.md` with step-by-step Ubuntu 24.04 setup + make targets
- ✅ Add `Makefile` with shortcuts: `make setup`, `make test`, `make lint`, `make api`
- ✅ Add `httpx` to `[dev]` dependencies (required by FastAPI TestClient)
- ✅ Bootstrap pip via `--without-pip` venv + `get-pip.py` (no sudo needed)
- ✅ Verified: **64 tests passing** (43 original + 21 new)
- ✅ Version bumped to `0.0.5`

**Commit:** `fix(dev): reliable one-command dev setup on Ubuntu 24.04; 64 tests passing`

---

## 🏗️ Phase 2 — Real Switch Engine (v0.1.0) ✅ COMPLETE

**Goal:** `gateos switch dev` performs a real OS-level environment switch — not dry-run.  
**Target:** April–May 2026 | **Branch:** `feat/real-switch-engine`  
**Owner:** Core Dev

### 2.1 — systemd Service Orchestration ✅
- ✅ `ServiceManager` class (`gateos_manager/services/__init__.py`)
- ✅ `start_services(manifest)` / `stop_services(manifest)` with dry-run support
- ✅ Required vs optional service failure handling
- ✅ `status(manifest)` for service health query
- ✅ 8 unit tests in `tests/test_service_manager.py`

### 2.2 — Kernel/Performance Profile Application ✅
- ✅ `ProfileApplicator` class (`gateos_manager/profile/__init__.py`)
- ✅ CPU governor application (`/sys/devices/system/cpu/*/cpufreq/scaling_governor`)
- ✅ GPU mode stub (logged; nvidia-smi / AMD sysfs integration planned)
- ✅ NIC priority stub (logged; tc/qdisc integration planned)
- ✅ `restore_defaults()` for rollback support
- ✅ 8 unit tests in `tests/test_profile_applicator.py`

### 2.3 — Switch Orchestrator Enhancement ✅
- ✅ `SwitchContext` dataclass (tracks containers, services, profile for rollback)
- ✅ Full activation pipeline: pre_switch → services → profile → containers → post_switch
- ✅ `_rollback()` function: stops containers + restores profile + stops services
- ✅ 5 unit tests in `tests/test_switch_orchestrator_enhanced.py`

### 2.4 — Real Container Orchestration ✅
- ✅ `ContainerManager._start_single()` issues real `podman run -d` with labels & volume mounts
- ✅ `--label gateos.env=<name>` + `--label gateos.managed=true` tagging on every container
- ✅ Top-level `manifest.mounts` + per-container `spec.mounts` both applied as `-v` flags
- ✅ Timeout handling via `subprocess.TimeoutExpired` (30 s start, 15 s stop)
- ✅ Return-code checking: logs stderr + emits `status=error` on non-zero exit
- ✅ Stop: `podman stop` then `podman rm --force` (best-effort, always resolves state)
- ✅ `GATEOS_CONTAINER_START_TIMEOUT` / `GATEOS_CONTAINER_STOP_TIMEOUT` env overrides
- ✅ `_detect_runtime()` gracefully falls back to dry-run when podman/docker absent

### 2.5 — Performance Benchmarks ✅
- ✅ `tests/test_perf_switch_latency.py` — 4 benchmark tests (1-ctr, 3-ctr, 10-ctr, 10×-stability)
- ✅ All pass well under 3 s budget in dry-run mode (typically < 50 ms)
- ✅ `@pytest.mark.benchmark` registered in `pyproject.toml` (run with `-m benchmark`)
- ✅ **68 tests passing** (was 64)

**Commit target:** `feat(containers): timeout, labels, volumes, return-code checking; benchmark tests`  
**Version bump:** `0.0.5 → 0.0.6`

---

## 🖥️ Phase 3 — GTK4 UI Shell (v0.1.0) ✅ COMPLETE

**Goal:** Functional desktop panel for environment switching.
**Completed:** March 5, 2026 | **Branch:** `feat/gtk4-ui-shell`

- ✅ Create `gateos_manager/ui/` package with `GTK_AVAILABLE` guard + `GtkNotAvailableError`
- ✅ `api_client.py` — `GateOSAPI` stdlib HTTP client (no extra deps) for Control API
- ✅ `env_list.py` — `EnvListPanel(Adw.PreferencesGroup)` + `EnvRow(Adw.ActionRow)` widgets
- ✅ `switch_button.py` — switch trigger with `Gtk.Spinner` + success/failure badge
- ✅ `status_bar.py` — active env + live API health indicator (5 s auto-poll)
- ✅ `tray.py` — `AppIndicatorTray` system tray icon (graceful degradation)
- ✅ `app.py` — `GateOSApp(Adw.Application)` main entry point; `GATEOS_UI_NO_DISPLAY` CI mode
- ✅ `data/gate-os-manager.desktop` — XDG desktop entry for autostart
- ✅ `gateos-ui` CLI entrypoint added to `pyproject.toml`
- ✅ `ui = ["PyGObject>=3.44.0"]` optional dependency group
- ✅ 32 new headless tests (full GTK mock → CI-safe); **100 tests passing**
- ✅ Version bumped to `0.1.0`

**Commit:** `feat(ui): GTK4 Adwaita shell — env list, switch panel, status bar, tray; 100 tests`

---

## 🐧 Phase 4 — Ubuntu ISO Builder (v0.2.0) ✅ COMPLETE

**Goal:** Bootable Gate-OS ISO installable on physical hardware.
**Completed:** March 5, 2026 | **Branch:** `feat/ubuntu-iso-builder`

- ✅ `scripts/build-iso.sh` — automated ISO build (download + chroot + squashfs + xorriso + checksum)
- ✅ `data/systemd/gateos-api.service` — hardened systemd unit (token auto-gen, restart policy)
- ✅ `gateos_manager/packaging/__init__.py` — `build_deb()`, `generate_preseed()`, `generate_postinstall_script()`
- ✅ `docs/installation/guide.md` — full install guide (ISO flash, overlay, post-config)
- ✅ `.github/workflows/build-iso.yml` — CI workflow: builds + publishes ISO on release tags
- ✅ 14 new packaging tests; **114 tests passing**
- ✅ Version bumped to `0.2.0`

**Commit:** `feat(iso): Ubuntu 24.04 LTS ISO builder, systemd service, packaging utils; 114 tests`

---

## 🔒 Phase 5 — Security Hardening (v0.3.0) ✅ COMPLETE

**Goal:** Production-grade security for environment isolation.  
**Completed:** 2026-03-05 | **147 tests passing**

- ✅ AppArmor profiles for all five environments (`profiles/apparmor/`)
  - `gateos-env-dev`, `gateos-env-gaming`, `gateos-env-security`, `gateos-env-design`, `gateos-env-media`
- ✅ seccomp profiles for containers (`profiles/seccomp/`)
  - `gateos-default.json` (OCI allowlist), `gateos-security.json` (strict, blocks kexec/mount/setns)
- ✅ Manifest signing module (`gateos_manager/security/signing.py`) — Ed25519 sign/verify/gen-keypair
- ✅ CLI subcommands: `gateos sign`, `gateos verify`, `gateos gen-keypair`
- ✅ `tests/test_security_hardening.py` — 33 tests (all passing)
- 📋 Named capability allowlist references (`allowlistRef` in schema) — deferred to Phase 6
- 📋 Network namespace segmentation per container — deferred to Phase 6
- 📋 Read-only root + ephemeral overlay for security environment — deferred to Phase 6

**Commit:** `feat(security): AppArmor profiles for all envs, seccomp configs, manifest signing; 147 tests`

---

## 📊 Phase 6 — Performance & Observability (v0.4.0) ✅ COMPLETE

**Goal:** Prometheus metrics, perf CI gate, structured observability.  
**Completed:** 2026-03-05 | **166 tests passing**

- ✅ `gateos_manager/telemetry/prometheus.py` — in-process MetricsRegistry (Counter, Gauge, Histogram)
- ✅ `GET /metrics` FastAPI endpoint (Prometheus text format 0.0.4)
- ✅ HTTP middleware auto-incrementing `gateos_api_requests_total`
- ✅ `gateos_switch_total` incremented on every switch
- ✅ `start_metrics_server()` daemon HTTP server on configurable port
- ✅ P99 rolling window (last 100 samples; no external deps)
- ✅ Perf CI gate: `test_switch_pipeline_completes_under_3_seconds` (marked `benchmark`)
- ✅ `tests/test_observability.py` — 19 tests (all passing)
- 📋 OpenTelemetry real exporter (replace stdout-only OTLP) — deferred to v0.5.0
- 📋 Memory delta measurement — deferred to v0.5.0

**Commit:** `feat(observability): Prometheus metrics, /metrics endpoint, perf CI gate; 166 tests`

---

## 📱 Phase 7 — Mobile Companion (v0.5.0) ✅ COMPLETE

**Goal:** WebSocket real-time status streaming and mobile-ready REST API.  
**Completed:** 2026-03-05 | **178 tests passing**

- ✅ `gateos_manager/api/websocket.py` — ConnectionManager, `GET /ws/status` endpoint, `broadcast_sync()`
- ✅ `POST /switch/{env}` now broadcasts `switch_done` to all WS clients
- ✅ WebSocket router integrated via `app.include_router(ws_router)`
- ✅ `docs/mobile/companion-api.md` — full WebSocket API reference + Flutter scaffold guide
- ✅ `tests/test_mobile_companion.py` — 12 tests (anyio async + TestClient WebSocket)
- ✅ Fixed `_flush_loop` in `emitter.py` — interval/batch-size now re-read per cycle
- 📋 Flutter Android app (basic switch UI) — Project v0.6.0
- 📋 Push notifications (FCM) on environment change — Project v0.7.0

**Commit:** `feat(mobile): WebSocket /ws/status endpoint, switch broadcast, mobile docs; 178 tests`

---

## 🚀 Phase 8 — Beta Release (v1.0.0-beta) ✅ COMPLETE

**Goal:** First public beta — OTA update stub, release notes, 198 tests passing.  
**Completed:** 2026-03-05 | **198 tests passing**

- ✅ `gateos_manager/updater.py` — OTA update module (check, apply, is_newer, schedule_apply stub)
- ✅ CLI: `gateos check-update`, `gateos apply-update [--yes]`
- ✅ `docs/release/v1.0.0-beta.md` — full beta release notes with migration guide
- ✅ `tests/test_beta_release.py` — 20 tests (all passing)
- ✅ Version: `0.5.0 → 1.0.0-beta`
- 📋 Flutter companion app (full UI) — v1.1.0
- 📋 OTA `schedule_apply()` via systemd — v1.1.0
- 📋 AppArmor auto-loader script — v1.1.0

**Commit:** `feat(beta): OTA update stub, beta release notes, 198 tests — v1.0.0-beta`

---

## 🏁 Project Status Summary

| Phase | Version | Tests | Coverage | Status |
|-------|---------|-------|----------|--------|
| Phase 0 — Foundation | v0.0.4 | 43 | — | ✅ Complete |
| Phase 1 — Dev Env Fix | v0.0.5 | 64 | — | ✅ Complete |
| Phase 2 — Real Switch Engine | v0.0.6 | 68 | — | ✅ Complete |
| Phase 3 — GTK4 UI Shell | v0.1.0 | 100 | — | ✅ Complete |
| Phase 4 — ISO Builder | v0.2.0 | 114 | — | ✅ Complete |
| Phase 5 — Security Hardening | v0.3.0 | 147 | — | ✅ Complete |
| Phase 6 — Observability | v0.4.0 | 166 | — | ✅ Complete |
| Phase 7 — Mobile Companion | v0.5.0 | 178 | — | ✅ Complete |
| Phase 8 — Beta Release | v1.0.0-beta | 198 | 82% | ✅ Complete |
| Phase 9 — Quality & Observability | v1.1.0 | **228** | **87%** | ✅ **Complete** |
| Phase 10 — Coverage Sprint | v1.2.0 | — | ≥90% | ⏳ Planned |
| Phase 11 — Documentation & Diagrams | v1.2.0 | — | — | ⏳ Planned |
| Phase 12 — Profile & System Completion | v1.3.0 | — | — | 📋 Planned |
| Phase 13 — Security Hardening v2 | v1.3.0 | — | — | 📋 Planned |
| Phase 14 — Mobile Companion App | v1.4.0 | — | — | 📋 Planned |
| Phase 15 — v1.0.0 Stable | v1.0.0 | — | — | 📋 Planned |

---

## 🔧 Phase 9 — Quality & Observability (v1.1.0) ✅ COMPLETE

**Goal:** Raise test coverage to 85%+, implement deferred v1.0.0-beta stubs, launch docs site.  
**Completed:** 2026-03-05 | **228 tests passing** | **87% coverage**

### 9.1 — Test Coverage
- ✅ Add `TestGateOSWindow` — construction + all callbacks (ui/app.py 35% → 70%+)
- ✅ Add `TestGateOSApp` — do_activate, do_startup, main() (ui/app.py)
- ✅ Add `TestAppIndicatorTrayWithIndicator` — indicator code paths (ui/tray.py 58% → 80%+)
- ✅ New `tests/test_watch_reloader.py` — start_watch() full coverage (53% → 100%)

### 9.2 — Feature Completions (from v1.0.0-beta backlog)
- ✅ `schedule_apply()` — systemd drop-in + flag file fallback (was NotImplementedError stub)
- ✅ `scripts/load-apparmor-profiles.sh` — auto-loader with enforce/complain modes
- ✅ `gateos_manager/telemetry/otlp.py` — real OTLP/HTTP JSON exporter (spans + logs + batch)
- ✅ `mkdocs.yml` — MkDocs Material documentation site scaffold
- ✅ `docs/index.md` — project home page
- ✅ `docs/observability/otlp.md` — OTLP integration guide

### 9.3 — Deferred to Next Phases
- 📋 GPU mode real implementation (nvidia-smi / AMD sysfs in ProfileApplicator) → Phase 12
- 📋 NIC priority (tc/qdisc integration) → Phase 12
- 📋 `allowlistRef` named capability in manifest schema → Phase 12
- 📋 Network namespace per-container isolation → Phase 12
- 📋 Flutter companion app scaffold (Android) → Phase 14
- 📋 Push notifications (FCM) on environment change → Phase 14
- 📋 OpenTelemetry auto-instrumentation for switch pipeline spans → Phase 10

---

---

## 🧪 Phase 10 — Coverage Sprint (v1.2.0) ⏳ PLANNED

**Goal:** Raise all modules to 90%+ coverage; close instrumentation gaps.  
**Target:** Q2 2026 | **Target:** ≥ 90% total

### 10.1 — Module Coverage Targets
- ⏳ `containers/manager.py` 50% → 90%+ — mock `subprocess` / podman calls for lines 130-216
- ⏳ `services/__init__.py` 67% → 90%+ — mock `systemctl` start/stop/status (lines 85-203)
- ⏳ `cli.py` 73% → 90%+ — exercise `sign`, `verify`, `gen-keypair`, `apply-update` commands (lines 56-150)
- ⏳ `updater.py` 80% → 95%+ — mock dpkg/systemd in schedule_apply paths (lines 163-227)

### 10.2 — Instrumentation
- ⏳ OpenTelemetry auto-instrumentation decorator for `SwitchOrchestrator.activate()`
- ⏳ Span/trace IDs injected into structured log records
- ⏳ `otlp.py` module coverage added to CI gate

---

## 📝 Phase 11 — Documentation & Diagrams (v1.2.0) ✅ COMPLETED

**Goal:** Bring all docs stubs to production quality; add architecture diagrams; deploy docs site.  
**Completed:** March 2026

### 11.1 — Architecture Diagrams (docs/diagrams/)
- ✅ `system-architecture.md` — Mermaid C4/component diagram (Layer: Kernel → Core Services → Env Manager → Containers → UI)
- ✅ `env-switch-sequence.md` — Mermaid sequence diagram (User → UI → Orchestrator → ServiceManager → ContainerManager)
- ✅ `module-boundaries.md` — Mermaid dependency graph of all `gateos_manager/` subpackages
- ✅ `api-flow.md` — REST + WebSocket request/response flow diagram

### 11.2 — Outdated Doc Updates
- ✅ `docs/architecture/overview.md` — inline current tech stack + Mermaid layer diagram; remove stubs
- ✅ `docs/roadmap/milestones.md` — reflect all completed phases and new roadmap to v1.0.0 Stable
- ✅ `docs/plan/project-plan.md` — update milestone table (many ❌ now ✅)
- ✅ `docs/plan/requirements.md` — update traceability matrix to reflect implemented items
- ✅ `docs/product/features.md` — replaced stub with real feature spec + MoSCoW table
- ✅ `docs/business/vision-mission.md` — filled in real vision/mission/value proposition text
- ✅ `docs/business/market-analysis.md` — real competitive landscape section
- ✅ `docs/security/threat-model.md` — added current controls v1.2.0 and planned v1.3.0
- ✅ `docs/architecture/supply-chain.md` — updated manifest signing status to ✅ Done

### 11.3 — Documentation Site
- ✅ Deploy MkDocs Material site to GitHub Pages (`mkdocs gh-deploy`)
- ✅ Fill in all navigation stubs in `mkdocs.yml` (13 missing pages created)
- ✅ Added getting-started tutorial covering `make setup` → `gateos validate` → `gateos api`
- ⏳ API reference page auto-generated from FastAPI OpenAPI schema (v1.3.0)

### 11.4 — New Pages Created (filling mkdocs.yml stubs)
- ✅ `docs/getting-started/quickstart.md`
- ✅ `docs/getting-started/configuration.md`
- ✅ `docs/architecture/environments.md`
- ✅ `docs/architecture/switch-engine.md`
- ✅ `docs/security/overview.md`
- ✅ `docs/security/apparmor.md`
- ✅ `docs/security/signing.md`
- ✅ `docs/observability/metrics.md`
- ✅ `docs/ota/how-it-works.md`
- ✅ `docs/ota/schedule-apply.md`
- ✅ `docs/contributing.md`
- ✅ `docs/plugins/plugin-guide.md`
- ✅ `docs/release-checklist.md`
- ✅ `docs/changelog.md`

---

## ⚙️ Phase 12 — Profile & System Completion (v1.3.0) 📋 PLANNED

**Goal:** Real hardware profile application; security schema completions.  
**Target:** Q3 2026

### 12.1 — Hardware Profiles (gateos_manager/profile/__init__.py)
- 📋 GPU mode: real `nvidia-smi -pm 1` / AMD `/sys/class/drm/card0/device/power_dpm_state`
- 📋 NIC priority: `tc qdisc add dev <nic> root tbf rate <limit>` per environment
- 📋 CPU governor validation: guard against missing cpufreq sysfs with fallback log
- 📋 Power profile: `powerprofilesctl set performance/balanced/power-saver`

### 12.2 — Manifest Schema Completions
- 📋 `allowlistRef` field in `data/schema/environment-manifest.schema.json` (named allowlist refs)
- 📋 Network namespace per-container: `networkNamespace` field in container spec
- 📋 Schema version bump → v0.2.0 + migration hook in `loader.py`

### 12.3 — DDE Integration
- 📋 Shell adapter interface (`gateos_manager/ui/shell_adapter.py`) — abstract `on_switch()` callback
- 📋 DDE panel plugin stub (env list widget for Deepin taskbar)
- 📋 `scripts/install-dde.sh` update for Ubuntu 24.04 Deepin PPA

---

## 🔐 Phase 13 — Security Hardening v2 (v1.3.0) 📋 PLANNED

**Goal:** Harden remaining threat model mitigations; supply chain integrity.  
**Target:** Q3 2026

### 13.1 — API Security
- 📋 API token rotation endpoint (`POST /auth/rotate-token`)
- 📋 OIDC-backed auth option (Keycloak / Dex integration stub)
- 📋 WebSocket auth (pass bearer token on connect, currently unauthenticated)
- 📋 Rate limit per-IP with configurable window via env vars

### 13.2 — Plugin Sandbox
- 📋 Plugin signature verification before entry-point load (`signing.py` integration)
- 📋 Plugin process isolation (run in subprocess with restricted capabilities)
- 📋 `GATEOS_ALLOW_UNSIGNED_PLUGINS=false` flag (opt-in for dev)

### 13.3 — Container Supply Chain
- 📋 Digest pin enforcement in manifests (`image` field validates `@sha256:` or warn)
- 📋 SLSA provenance attestation for Gate-OS Python package (GitHub Actions)
- 📋 SBOM transparency log — emit `sbom_generated` telemetry event after Syft run
- 📋 Read-only root + ephemeral overlay for `security` environment containers

### 13.4 — Telemetry TLS
- 📋 OTLP exporter TLS support (`GATEOS_OTLP_TLS_CERT` env var)
- 📋 PII redaction filter for structured log fields

---

## 📱 Phase 14 — Mobile Companion App (v1.4.0) 📋 PLANNED

**Goal:** Functional Flutter Android app for remote environment control.  
**Target:** Q3-Q4 2026

### 14.1 — Flutter App Scaffold
- 📋 `mobile/` directory with Flutter project (`lib/main.dart`, `pubspec.yaml`)
- 📋 WebSocket client connecting to `ws://gate-os.local:8088/ws/status`
- 📋 Environment list UI (Material Design, 5 env cards: dev/gaming/design/media/security)
- 📋 Switch button with loading state + success/failure toast
- 📋 Settings screen: host, port, API token

### 14.2 — Push Notifications
- 📋 FCM integration in Flutter app (Firebase Cloud Messaging)
- 📋 Gate-OS server-side push hook: on `switch_done` → FCM notify
- 📋 `GATEOS_FCM_SERVER_KEY` env var; graceful no-op if not set

### 14.3 — Mobile CI
- 📋 `.github/workflows/flutter.yml` — lint + test + APK build on PR
- 📋 GitHub release artifact: attach debug APK

---

## 🏁 Phase 15 — v1.0.0 Stable 📋 PLANNED

**Target:** Q4 2026

- 📋 v1.0.0 stable release (all phases 10-14 complete)
- 📋 Enterprise pilot: 2 organizations
- 📋 25+ community contributors
- 📋 Full documentation site live (MkDocs Material on GitHub Pages)
- 📋 GitHub Actions release pipeline: ISO build + APK + PyPI publish
- 📋 Security audit by external reviewer

---

## 📌 Immediate Next Actions (v1.2.0 Sprint)

```
Priority  Task                                                  Owner    Phase  Status
────────  ────────────────────────────────────────────────────  ───────  ─────  ──────
P0        containers/manager.py coverage 50%→90%               QA       10     ⏳ Next
P0        services/__init__.py coverage 67%→90%                 QA       10     ⏳ Next
P0        cli.py coverage 73%→90%                               QA       10     ⏳ Next
P0        Mermaid system architecture diagram                    Arch     11     ⏳ Next
P0        Mermaid env-switch sequence diagram                    Arch     11     ⏳ Next
P1        Deploy docs site (mkdocs gh-deploy)                    DevOps   11     ⏳ Next
P1        Update architecture/overview.md (stubs → real)        Arch     11     ⏳ Next
P1        Update roadmap/milestones.md (outdated)               PM       11     ⏳ Next
P1        Update docs/plan/project-plan.md milestone table       PM       11     ⏳ Next
P1        OpenTelemetry span decorator on SwitchOrchestrator     Core     10     ⏳ Next
P2        GPU real implementation (nvidia-smi / AMD sysfs)       Core     12     📋 Soon
P2        NIC priority tc/qdisc                                  Core     12     📋 Soon
P2        allowlistRef in manifest schema v0.2.0                Arch     12     📋 Soon
P2        Flutter Android app scaffold                           Mobile   14     📋 Soon

## 📈 Version History Summary

| Version | Tag | Date | Description |
|---------|-----|------|-------------|
| 0.0.1 | v0.0.1 | 2025-08 | Initial scaffold |
| 0.0.2 | v0.0.2 | 2025-08 | Schema + API foundation |
| 0.0.3 | v0.0.3 | 2025-08 | Telemetry batch, plugin discovery, schema versioning |
| 0.0.4 | v0.0.4 | 2025-08 | Rate limit fix, 43 tests, PyPI publish workflow |
| 0.0.5 | ✅ | 2026-03-05 | Dev toolchain fix + ServiceManager + ProfileApplicator + SwitchContext; 64 tests |
| 0.0.6 | ✅ | 2026-03-05 | Real container orchestration (timeout/labels/volumes) + benchmark tests; 68 tests |
| 0.1.0 | ✅ | 2026-03-05 | GTK4 UI shell (env list, switch panel, status bar, tray); 100 tests |
| 0.2.0 | ✅ | 2026-03-05 | Ubuntu ISO builder + systemd service + packaging utils; 114 tests |
| 0.3.0 | ✅ | 2026-03-05 | AppArmor + seccomp profiles, manifest signing; 147 tests |
| 0.4.0 | ✅ | 2026-03-05 | Prometheus metrics, /metrics endpoint, perf CI gate; 166 tests |
| 0.5.0 | ✅ | 2026-03-05 | WebSocket /ws/status, mobile companion; 178 tests |
| 1.0.0-beta | ✅ v1.0.0-beta | 2026-03-05 | OTA stub, beta release notes, 198 tests |
| 1.1.0 | ✅ v1.1.0 | 2026-03-05 | Coverage 87%, schedule_apply(), OTLP exporter, docs scaffold; 228 tests |
| 1.2.0 | ⏳ | 2026-Q2 | Coverage Sprint ≥90%, architecture diagrams, docs site deployed |
| 1.3.0 | 📋 | 2026-Q3 | GPU/NIC profiles, allowlistRef, network ns, Security Hardening v2 |
| 1.4.0 | 📋 | 2026-Q3 | Flutter Android app, FCM push, mobile CI |
| 1.0.0 | 📋 | 2026-Q4 | Stable release, enterprise pilot, 25+ contributors |


---

*Auto-updated with each commit. See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.*
