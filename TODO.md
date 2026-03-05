# Gate-OS — Task Board & Work Plan

> Living document — updated after every completed phase.  
> Last updated: **March 5, 2026**  
> Current version: **0.0.4** → Next target: **0.1.0-alpha** (Team Alpha ISO)

---

## Legend

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

## 🔧 Phase 1 — Dev Environment Fix (v0.0.5) 🔄 IN PROGRESS

**Goal:** Every team member can clone the repo and run tests in under 5 minutes.  
**Target:** March 2026 | **Branch:** `fix/dev-toolchain`

- ✅ Audit dev environment (pip/pytest not installed in base system)
- ✅ Update `docs/plan/project-plan.md` with full Ubuntu ISO roadmap
- 🔄 Add `.gitignore` entry for `package-lock.json`
- ⏳ Fix `setup-dev-env.sh` to work without pre-installed pip (use `ensurepip`)
- ⏳ Update `CONTRIBUTING.md` with step-by-step Ubuntu 24.04 setup
- ⏳ Add `Makefile` with shortcuts: `make setup`, `make test`, `make lint`, `make api`
- ⏳ Add `.python-version` file (3.11 recommended)
- ⏳ Verify all 43 tests pass on clean Ubuntu 24.04 install

**Commit target:** `fix(dev): reliable one-command dev setup on Ubuntu 24.04`  
**Version bump:** `0.0.4 → 0.0.5`

---

## 🏗️ Phase 2 — Real Switch Engine (v0.1.0) ⏳ PLANNED

**Goal:** `gateos switch dev` performs a real OS-level environment switch — not dry-run.  
**Target:** April–May 2026 | **Branch:** `feat/real-switch-engine`  
**Owner:** Core Dev

### 2.1 — systemd Service Orchestration
- ⏳ Implement `ServiceManager` class (`gateos_manager/services/manager.py`)
- ⏳ `stop_conflicting_services(env_name)` — stops services from previous environment
- ⏳ `start_environment_services(manifest)` — starts services listed in manifest
- ⏳ Integrate with `switch/orchestrator.py` in real mode

### 2.2 — Real Container Orchestration
- ⏳ Replace dry-run `ContainerManager.start()` with real `podman run` commands
- ⏳ Add `--rm` flag for ephemeral containers on environment exit
- ⏳ Implement `ContainerManager.stop()` with `podman stop` + `podman rm`
- ⏳ Add timeout handling for container startup

### 2.3 — Kernel/Performance Profile Application
- ⏳ `ProfileApplicator` class: apply CPU governor, NIC priority, GPU mode from manifest
- ⏳ Write to `/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
- ⏳ Integrate with `switch/orchestrator.py`

### 2.4 — Rollback on Failure
- ⏳ Implement activation rollback: if switch fails mid-way, restore previous state
- ⏳ Add `SwitchContext` dataclass to track pre-switch state

### 2.5 — Tests & Benchmarks
- ⏳ Integration test: real switch with mock systemd (using `systemd` test fixtures)
- ⏳ Performance benchmark: measure switch latency (target < 3s)
- ⏳ Add `tests/test_perf_switch_latency.py`

**Commit target:** `feat(switch): real OS-level environment switching with systemd + podman`  
**Version bump:** `0.0.5 → 0.1.0`

---

## 🖥️ Phase 3 — GTK4 UI Shell (v0.2.0) ⏳ PLANNED

**Goal:** Functional desktop panel for environment switching.  
**Target:** May 2026 | **Branch:** `feat/gtk4-ui-shell`  
**Owner:** UI Dev

- ⏳ Create `gateos_manager/ui/` package
- ⏳ `app.py` — GTK4 `Adw.Application` main entry point
- ⏳ `env_list.py` — `Adw.PreferencesGroup` listing available environments
- ⏳ `switch_button.py` — switch trigger with loading spinner
- ⏳ `status_bar.py` — current environment + telemetry status
- ⏳ Integrate with Control API via local HTTP
- ⏳ System tray icon (AppIndicator) for quick-switch
- ⏳ Add `gateos-ui` CLI entrypoint in `pyproject.toml`
- ⏳ Desktop `.desktop` file for autostart

**Commit target:** `feat(ui): GTK4 Adwaita shell with environment list and switch panel`  
**Version bump:** `0.1.0 → 0.2.0`

---

## 🐧 Phase 4 — Ubuntu ISO Builder (v0.3.0) ⏳ PLANNED

**Goal:** Bootable Gate-OS ISO installable on physical hardware.  
**Target:** May–June 2026 | **Branch:** `feat/ubuntu-iso-builder`  
**Owner:** DevOps

- ⏳ Create `scripts/build-iso.sh` — automated ISO build script
- ⏳ Use `cubic` or `live-build` on Ubuntu 24.04 LTS base
- ⏳ Build `.deb` package for `gateos-manager` (`hatch build` → deb conversion)
- ⏳ Add `gateos-manager` to ISO's preseed/postinstall
- ⏳ Auto-configure systemd service `gateos-api.service` on boot
- ⏳ Add DDE session option (complete `install-dde.sh` integration)
- ⏳ Create `docs/installation/` guide (ISO download + Ventoy/USB instructions)
- ⏳ Add GitHub Actions workflow: `.github/workflows/build-iso.yml`
- ⏳ Internal team ISO distribution process

**Commit target:** `feat(iso): Ubuntu 24.04 LTS base + gateos-manager overlay build script`  
**Version bump:** `0.2.0 → 0.3.0`

---

## 🔒 Phase 5 — Security Hardening (v0.4.0) 📋 PLANNED

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
Priority  Task                                          Owner
────────  ────────────────────────────────────────────  ──────
P0        Fix setup-dev-env.sh (ensurepip)              DevOps
P0        Update CONTRIBUTING.md (Ubuntu 24.04 steps)   PM
P0        Add Makefile (make setup / test / lint)        DevOps
P1        ServiceManager stub (systemd integration)      Core
P1        Real ContainerManager.start() with podman      Core  
P1        GTK4 window scaffold (Adw.Application)         UI
P1        build-iso.sh first draft (cubic-based)         DevOps
P2        Performance benchmark test file                QA
P2        AppArmor profile for dev environment           Sec
```

---

## 📈 Version History Summary

| Version | Tag | Date | Description |
|---------|-----|------|-------------|
| 0.0.1 | v0.0.1 | 2025-08 | Initial scaffold |
| 0.0.2 | v0.0.2 | 2025-08 | Schema + API foundation |
| 0.0.3 | v0.0.3 | 2025-08 | Telemetry batch, plugin discovery, schema versioning |
| 0.0.4 | v0.0.4 | 2025-08 | Rate limit fix, 43 tests, PyPI publish workflow |
| 0.0.5 | — | 2026-03 | Dev toolchain fix + Ubuntu ISO roadmap docs 🔄 |
| 0.1.0 | — | 2026-05 | Real switch engine (systemd + podman) ⏳ |
| 0.2.0 | — | 2026-05 | GTK4 UI shell ⏳ |
| 0.3.0 | — | 2026-06 | Ubuntu 24.04 ISO builder ⏳ |
| 0.4.0 | — | 2026-07 | Security hardening ⏳ |
| 0.5.0 | — | 2026-07 | Perf & observability ⏳ |
| 0.6.0 | — | 2026-08 | Mobile companion ⏳ |
| 1.0.0-beta | — | 2026-09 | Public beta 📋 |
| 1.0.0 | — | 2026-Q4 | Stable release 📋 |

---

*Auto-updated with each commit. See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.*
