# Gate-OS — Task Board & Work Plan

> Living document — updated after every completed phase.  
> Last updated: **March 5, 2026**  
> Current version: **0.2.0** → Next target: **0.3.0** (Security Hardening)

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

## 🔒 Phase 5 — Security Hardening (v0.3.0) ⏳ PLANNED

**Goal:** Production-grade security for environment isolation.  
**Target:** June–July 2026 | **Branch:** `feat/security-hardening`  
**Owner:** Security

- 📋 AppArmor profiles for each environment (`profiles/apparmor/`)
- 📋 seccomp profiles for containers (`profiles/seccomp/`)
- 📋 Manifest signing CLI stub (`gateos sign` / `gateos verify`)
- 📋 Named capability allowlist references (`allowlistRef` in schema)
- 📋 Network namespace segmentation per container
- 📋 Read-only root + ephemeral overlay for security environment
- 📋 Audit log export to telemetry pipeline

**Commit target:** `feat(security): AppArmor profiles, manifest signing, network isolation`  
**Version bump:** `0.3.0 → 0.4.0`

---

## 📊 Phase 6 — Performance & Observability (v0.5.0) 📋 PLANNED

**Target:** July 2026

- 📋 OpenTelemetry exporter (replace stdout-only)
- 📋 Switch latency dashboard (Prometheus metrics endpoint)
- 📋 Automated perf regression test in CI (fail if > 3s)
- 📋 Memory delta measurement per environment
- 📋 GPU resource monitoring hook

---

## 📱 Phase 7 — Mobile Companion (v0.6.0) 📋 PLANNED

**Target:** August 2026

- 📋 Flutter Android app scaffold
- 📋 WebSocket endpoint for real-time status
- 📋 Remote switch trigger from mobile
- 📋 Environment status notifications

---

## 🚀 Phase 8 — Beta Release (v1.0.0-beta) 📋 PLANNED

**Target:** August–September 2026

- 📋 All 4 core environments working: gaming, dev, design, media
- 📋 Security environment (Kali toolkit) hardened
- 📋 Public ISO download page
- 📋 OTA update mechanism
- 📋 < 3s switch latency validated + published benchmarks
- 📋 Community: open beta waitlist
- 📋 Release notes + migration guide

---

## 🏁 Phase 9 — v1.0 Launch 📋 PLANNED

**Target:** Q4 2026

- 📋 v1.0.0 stable release
- 📋 Enterprise pilot: 2 organizations
- 📋 25+ community contributors
- 📋 Full documentation site (MkDocs)

---

## 📌 Immediate Next Actions (This Week)

```
Priority  Task                                          Owner    Status
────────  ────────────────────────────────────────────  ───────  ──────
P0        Fix setup-dev-env.sh (ensurepip)              DevOps   ✅ Done
P0        Update CONTRIBUTING.md (Ubuntu 24.04 steps)   PM       ✅ Done
P0        Add Makefile (make setup / test / lint)        DevOps   ✅ Done
P1        ServiceManager (systemd integration)           Core     ✅ Done
P1        Real ContainerManager.start() with podman      Core     ✅ Done
P1        Performance benchmark test file                QA       ✅ Done
P1        GTK4 window scaffold (Adw.Application)         UI       ✅ Done
P1        Full GTK4 UI shell (env list/switch/tray)      UI       ✅ Done
P1        build-iso.sh first draft (cubic-based)         DevOps   ⏳ Next
P2        AppArmor profile for dev environment           Sec      📋 Soon

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
| 0.3.0 | — | 2026-06 | Security hardening ⏳ |
| 0.3.0 | — | 2026-06 | Ubuntu 24.04 ISO builder ⏳ |
| 0.4.0 | — | 2026-07 | Security hardening ⏳ |
| 0.5.0 | — | 2026-07 | Perf & observability ⏳ |
| 0.6.0 | — | 2026-08 | Mobile companion ⏳ |
| 1.0.0-beta | — | 2026-09 | Public beta 📋 |
| 1.0.0 | — | 2026-Q4 | Stable release 📋 |

---

*Auto-updated with each commit. See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.*
