<!-- Gate-OS Project Plan -->
# Gate-OS Project Plan

## Purpose

Single source of truth for scope, prioritized requirements, milestones, and
progress tracking ("tracker").

**Last Updated:** March 2026 — Full audit + Ubuntu-based installable OS roadmap added. Team adoption path defined.

---

## Base OS Decision: Ubuntu LTS ✅ Confirmed

**Gate-OS is built on Ubuntu LTS** — this is already documented in the architecture overview and is the correct choice:

| Why Ubuntu LTS? | Detail |
|-----------------|--------|
| **Stability** | LTS = 5 years security support; safe foundation for production |
| **Ecosystem** | Largest app/driver compatibility; PPA support; Snap + Deb |
| **Hardware Support** | Widest hardware driver coverage out of the box |
| **Container Native** | Docker & Podman run natively; systemd fully integrated |
| **Custom ISO Tooling** | `cubic`, `live-build`, `debootstrap` — mature Ubuntu customization tools |
| **Gaming** | Steam officially targets Ubuntu; Proton/Wine best support |
| **Enterprise** | Canonical commercial support available when needed |
| **DDE Available** | Deepin Desktop packages exist in Ubuntu repos |

**Recommended Base:** Ubuntu 24.04 LTS "Noble Numbat" (latest LTS as of 2024, supported until 2029)

---

## Vision (Summary)

Deliver a universal Linux distribution enabling deterministic, low‑latency
switching across specialized environments (gaming, dev, design, media, security)
backed by a declarative manifest model, open governance, and enterprise-ready security.

---

## Project Health Assessment (March 2026)

### ✅ Strengths

| Area | Detail |
|------|--------|
| Architecture | Solid layered design: Kernel → Core Services → Env Manager → Containers → UI |
| Manifest Schema | Well-defined JSON Schema (v0.1.0) with versioning & migration hooks |
| Security Foundation | Capability allowlist enforcement, isolationLevel policy via `security/policy.py` |
| Modular Python Core | Clean separation: `manifest/`, `switch/`, `containers/`, `api/`, `security/`, `telemetry/` |
| REST Control API | FastAPI-based API with token auth, rate limiting, correlation IDs |
| Telemetry Pipeline | Structured JSON events, OTLP-compatible batch queue, correlation IDs |
| Plugin System | Entry-point based `pre_switch` / `post_switch` / `shutdown` hooks |
| CI & SBOM | Grype + Syft security scanning baked into CI pipeline |
| Test Coverage | 15+ test files covering manifest, switch, security policy, containers, telemetry |
| Documentation | Comprehensive docs structure: architecture, security, roadmap, API, environments |

### ⚠️ Weaknesses & Gaps

| Area | Gap | Priority |
|------|-----|----------|
| UI Shell | GTK4 UI not yet implemented — only placeholders | HIGH |
| Container Runtime | `ContainerManager` is in dry-run mode; no real orchestration with systemd/cgroups | HIGH |
| Environment Switching | Real OS-level switch (suspend services, apply kernel params, GPU handoff) not implemented | HIGH |
| Test Environment | `pytest` not installed in base system; CI setup incomplete locally | HIGH |
| Schema Version | Schema still at `v0.1.0` / draft; `apiVersion` pattern is not released | MEDIUM |
| Performance Tests | No benchmarking harness for the < 3s switch latency KPI | MEDIUM |
| Packaging | No ISO builder, no GRUB/kernel customization scripts | MEDIUM |
| Mobile Companion | API designed but no Flutter client prototype | MEDIUM |
| Manifest Signing | Planned but not started — supply chain risk | MEDIUM |
| DDE Integration | Install script present but shell adapter interface not implemented | MEDIUM |
| Network QoS | Not started; important for gaming/streaming environments | LOW |
| Docs Completeness | Several docs are stubs with placeholders (market analysis, vision/mission) | LOW |
| Architecture Diagrams | Only ASCII placeholder; `.drawio` files not yet created | LOW |
| GPU Scheduling | No GPU resource allocation per profile | LOW |

---

## Success Criteria (v1 Launch)

| KPI | Target | Measurement Method | Status |
|-----|--------|--------------------|--------|
| Switch latency | < 3s median | Instrumented telemetry event pair (start/ready) | ⏳ Not measured |
| Activation reliability | > 99% success | Switch outcomes log | ⏳ Dry-run only |
| Manifest validation coverage | 100% schema required fields | CI + test suite | ✅ Schema in place |
| Critical vulnerabilities (prod build) | 0 High/Critical | Grype scan pipeline | ✅ CI step exists |
| Onboarding time (contributor) | < 30m | Developer survey | ⚠️ pip not configured |
| Test line coverage | ≥ 80% | pytest-cov report | ⏳ Not measured |

---

## Scope (v1 Included)

- Environment manifest schema + validator (Python) ✅
- Environment Manager (activation lifecycle, basic hooks) 🔄
- Two reference environments (dev, gaming) ✅ manifests exist
- Basic UI shell placeholder (GTK4) with environment list + switch button ❌ not implemented
- Telemetry stub (stdout JSON events) + structured logs ✅
- Security baseline: isolationLevel policy enforcement scaffold ✅
- CI: lint, tests, coverage, SBOM, vuln scan 🔄 partial
- Real container/service orchestration on switch ❌ dry-run only
- REST Control API (FastAPI) ✅

## Out of Scope (v1)

- Full UI theming & design system
- Advanced GPU scheduling
- Full SELinux/AppArmor policy sets (placeholders only)
- Network QoS prioritization
- Packaging for multiple distros (Ubuntu base only)
- ISO image builder

---

## Milestones & Tracker (Updated)

| ID | Milestone | Description | Original Target | Updated Target | Status | Owner |
|----|-----------|-------------|-----------------|----------------|--------|-------|
| M1 | Schema Foundation | JSON Schema v0.1.0 + examples | 2025-09 | — | ✅ Done | Arch |
| M2 | Manager Core | load/validate + switch orchestration skeleton | 2025-10 | — | ✅ Done (skeleton) | Core |
| M3 | UI Shell MVP | GTK4: list envs + trigger switch button | 2025-11 | 2026-04 | ❌ Not Started | UI |
| M4 | Telemetry Stub | Emit switch events + basic metrics | 2025-11 | — | ✅ Done | Core |
| M5 | Security Baseline | isolationLevel enforcement hooks | 2025-12 | — | ✅ Done (stub) | Sec |
| M6 | Coverage 80% | Unit tests for manager & schema helpers | 2025-12 | 2026-04 | 🔄 In Progress | QA |
| M7 | Packaging Alpha | Image build + install script | 2026-01 | 2026-05 | ❌ Not Started | DevOps |
| M8 | Security Env | Security (Kali tools) manifest + hardening | 2026-01 | — | ✅ Done (manifest) | Sec |
| M9 | DDE Integration | Deepin Desktop session support | 2026-02 | 2026-05 | 🔄 Script exists | UI |
| M10 | Mobile Companion Alpha | Android app API + Flutter prototype | 2026-03 | 2026-06 | ❌ Not Started | Mobile |
| M11 | Security Policy v1 | Capability allowlist + validation errors | 2026-03 | — | ✅ Done (v0) | Sec |
| M12 | Real Switch Engine | OS-level env switch: suspend services, apply cgroups/kernel params | — | 2026-05 | ❌ Critical Gap | Core |
| M13 | Perf Test Harness | Automated latency benchmark (target < 3s) | — | 2026-04 | ❌ Not Started | QA |
| M14 | Dev Environment Setup | Fix pip/pytest for contributor onboarding | — | 2026-03 | 🔄 Immediate | DevOps |
| M15 | Manifest Signing | CLI stub for signature verification | — | 2026-06 | ❌ Not Started | Sec |
| M16 | Architecture Diagrams | .drawio files: system, sequence, module boundaries | — | 2026-04 | ❌ Not Started | Arch |
| M17 | 1.0 Public Beta | Bootable system + 2 working environments | — | 2026-08 | ❌ Planned | PM |

Status Legend: ✅ Done / 🔄 In Progress / ❌ Not Started / ⚠️ At Risk / 🔴 Blocked

---

## Immediate Action Items (Q1–Q2 2026)

These are the highest-priority unblocking tasks:

1. **Fix Dev Toolchain** — Install `python3-pip`, `pytest`, set up virtualenv; update `CONTRIBUTING.md` with exact setup steps.
2. **Implement Real Switch Engine** — Replace dry-run `ContainerManager` with real `podman`/`docker` orchestration + systemd service management.
3. **Build GTK4 UI Shell** — Implement the environment list panel and switch button.
4. **Add Performance Test Harness** — Measure switch latency end-to-end against the < 3s KPI.
5. **Complete Architecture Diagrams** — Create `.drawio` assets referenced in docs but missing.
6. **Fill Documentation Stubs** — Replace placeholder text in `vision-mission.md`, `market-analysis.md` with real content.

---

## Installable OS Roadmap — Ubuntu 24.04 LTS Base

This section defines the path from the current Python manager scaffold to a **real installable Gate-OS system** that the team can use and develop on physical hardware.

### Architecture: Two-Layer Approach

```
┌─────────────────────────────────────────────────────────┐
│                  Gate-OS ISO Image                       │
│                                                         │
│  Layer 1: Ubuntu 24.04 LTS Base (kernel + drivers)      │
│  Layer 2: Gate-OS Manager + UI + Environment Profiles   │
│                                                         │
│  Install Method: Ubiquity (Ubuntu installer)             │
│  or: debian-installer + preseed for unattended          │
└─────────────────────────────────────────────────────────┘
```

### Phase A — Team Alpha (Target: May 2026) 🎯

**Goal:** Team members can install Gate-OS on their machines and use it daily.

| Task | Description | Tool/Method | Owner |
|------|-------------|-------------|-------|
| A1 | Bootstrap Ubuntu 24.04 LTS base | Download Ubuntu ISO | DevOps |
| A2 | Build custom ISO with `cubic` | Add gateos-manager package to Ubuntu live image | DevOps |
| A3 | Auto-install `gateos-manager` on boot | Add `.deb` package or pip install via preseed/postinstall | Core |
| A4 | Create `gate-os-installer` post-install script | Installs Gate-OS layer on top of Ubuntu base | DevOps |
| A5 | Real switch engine (M12) | systemd service suspend/resume + container start | Core |
| A6 | GTK4 UI panel (M3) | Environment list + switch button visible on desktop | UI |
| A7 | DDE session option (M9) | `install-dde.sh` completed + session file | UI |
| A8 | Dev environment manifest working | `gateos switch dev` starts real toolchain containers | Core |
| A9 | Team onboarding doc | Step-by-step: download ISO → install → first switch | PM |

#### Tools for Building Ubuntu Custom ISO

```bash
# Option 1: cubic (GUI-based, recommended for team ease)
sudo apt install cubic
# Open Ubuntu 24.04 ISO → add gateos packages → export new ISO

# Option 2: live-build (scriptable, CI-friendly)
sudo apt install live-build
lb config --distribution noble --archive-areas "main contrib non-free"
# Copy gateos-manager into chroot → lb build

# Option 3: minimal overlay (fastest prototype)
# Install Ubuntu 24.04 normally → run gate-os postinstall script
curl -fsSL https://install.gateos.io/setup.sh | bash  # (future)
```

### Phase B — Beta Release (Target: August 2026) 🚀

**Goal:** Public beta: downloadable ISO, full environment switching, stable team workflows.

| Task | Description | Status |
|------|-------------|--------|
| B1 | Automated ISO build via GitHub Actions | CI produces fresh ISO on each release tag |
| B2 | Gaming environment working end-to-end | Steam + Proton + GPU profile via manifest |
| B3 | Security environment working | Kali tools in isolated containers |
| B4 | Performance: < 3s switch latency validated | Telemetry benchmark in CI |
| B5 | OTA update mechanism | Gate-OS manager self-updates without reinstall |
| B6 | Manifest signing (M15) | Signed bundles verified before activation |
| B7 | Public beta waitlist + download page | Marketing + community |

### Phase C — v1.0 Launch (Target: Q4 2026) 🏁

**Goal:** Stable, versioned, production-ready release on Ubuntu 24.04 LTS.

| Task | Description |
|------|-------------|
| C1 | 4 environments fully functional: gaming, dev, design, media |
| C2 | Security environment (Kali toolkit) hardened |
| C3 | Mobile companion API live (Android app alpha) |
| C4 | Full security audit passed (AppArmor profiles + Grype clean) |
| C5 | Community: first 25 external contributors |
| C6 | Enterprise pilot: 2 organizations using Gate-OS |

---

## Team Adoption Plan (Immediate)

To start using Gate-OS for daily development **right now** (before ISO is ready):

### Step 1 — Fix Dev Environment (This Week)

```bash
# On Ubuntu 24.04 (or any Ubuntu 22.04+):
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
cd /path/to/Gate-OS
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -q   # should show 43+ passing tests
```

### Step 2 — Run Gate-OS Manager Locally (Week 1)

```bash
# Validate manifests
gateos validate examples/environments/*.yaml

# Start the Control API
gateos api --host 127.0.0.1 --port 8088

# Generate an API token
gateos gen-token --length 40 > .api.token
export GATEOS_API_TOKEN=$(cat .api.token)
export GATEOS_API_TOKEN_FILE=.api.token
```

### Step 3 — Each Team Member Contributes (Week 1–4)

| Role | First Task | Branch |
|------|-----------|--------|
| Core Dev | Implement real `ContainerManager.start()` with podman | `feat/real-container-switch` |
| UI Dev | Create GTK4 window with `Adw.ApplicationWindow` + env list | `feat/gtk4-ui-shell` |
| DevOps | Build Ubuntu 24.04 + gateos overlay with cubic | `feat/ubuntu-iso-builder` |
| QA | Add performance benchmark test (measure switch latency) | `feat/perf-test-harness` |
| Sec | Implement AppArmor profile stub for dev environment | `feat/apparmor-dev-profile` |

### Step 4 — Internal ISO for Team (Month 2)

Once A2–A6 are done, DevOps builds and distributes the internal ISO:
- Team installs on dedicated machines or VMs
- Daily use: `gateos switch dev` for coding, `gateos switch gaming` for testing
- Feedback loop: file issues → fix → rebuild ISO weekly

---

## Risk Register (Updated)

| Risk | Impact | Likelihood | Mitigation | Owner | Status |
|------|--------|------------|-----------|-------|--------|
| Scope creep UI | Delay core | M | Strict v1 scope; UI is last after engine | PM | Open |
| Security gap (policies) | Trust erosion | M | Stub policies v0 shipped; v1 allowlistRef next | Sec | Open |
| Performance regressions | Latency > 3s target | H | Add perf harness (M13) before engine work | Core | **At Risk** |
| Limited contributors | Slow velocity | H | Fix onboarding (M14); improve CONTRIBUTING.md | PM | Open |
| No real switch engine | Product unusable | H | M12 is critical path — schedule immediately | Core | **At Risk** |
| Missing diagrams | Architecture misalignment | L | Schedule diagram sprint (M16) | Arch | Open |
| Python env setup broken | No contributor can run tests | H | Fix pip/venv setup this sprint | DevOps | **At Risk** |
| ISO build not automated | Manual overhead slows releases | M | Add GitHub Actions ISO job in Phase B | DevOps | Open |

---

## Requirement Set

See `requirements.md` for full details. Traceability matrix links each requirement to artifacts & tests.

## Change Control

Material scope changes require RFC (see `rfcs/`). Update this plan via PR referencing impacted requirement IDs.

## Reporting Cadence

Bi-weekly progress update referencing milestones table & risk changes.

---
**Last Updated:** March 2026 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
