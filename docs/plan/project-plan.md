<!-- Gate-OS Project Plan -->
# Gate-OS Project Plan

## Purpose
Single source of truth for scope, prioritized requirements, milestones, and progress tracking ("tracker").

## Vision (Summary)
Deliver a universal Linux distribution enabling deterministic, low‑latency switching across specialized environments (gaming, dev, design, media) backed by a declarative manifest model and open governance.

## Success Criteria (v1 Launch)
| KPI | Target | Measurement Method |
|-----|--------|--------------------|
| Switch latency | < 3s median | Instrumented telemetry event pair (start/ready) |
| Activation reliability | > 99% success | Switch outcomes log |
| Manifest validation coverage | 100% schema required fields | CI + test suite |
| Critical vulnerabilities (prod build) | 0 High/Critical | Grype scan pipeline |
| Onboarding time (contributor) | < 30m | Developer survey |

## Scope (v1 Included)
- Environment manifest schema + validator (Python)
- Environment Manager (activation lifecycle, basic hooks)
- Two reference environments (dev, gaming)
- Basic UI shell placeholder (GTK4) with environment list + switch button
- Telemetry stub (stdout JSON events) + structured logs
- Security baseline: isolationLevel policy enforcement scaffold
- CI: lint, tests, coverage, SBOM, vuln scan

## Out of Scope (v1)
- Full UI theming & design system
- Advanced GPU scheduling
- Full SELinux/AppArmor policy sets (placeholders only)
- Network QoS prioritization
- Packaging for multiple distros (Ubuntu base only)

## Milestones & Tracker
| ID | Milestone | Description | Target | Status | Owner |
|----|-----------|-------------|--------|--------|-------|
| M1 | Schema Foundation | Finalize JSON Schema & examples | 2025-09 | Done | Arch |
| M2 | Manager Core | load/validate + switch orchestration skeleton | 2025-10 | In Progress | Core |
| M3 | UI Shell MVP | List envs + trigger switch | 2025-11 | Planned | UI |
| M4 | Telemetry Stub | Emit switch events + basic metrics | 2025-11 | Planned | Core |
| M5 | Security Baseline | isolationLevel enforcement hooks | 2025-12 | Planned | Sec |
| M6 | Coverage 80% | Unit tests for manager & schema helpers | 2025-12 | Planned | QA |
| M7 | Packaging Alpha | Image build + install script | 2026-01 | Planned | DevOps |

Status Legend: Done / In Progress / Planned / At Risk / Blocked.

## Risk Register (Top)
| Risk | Impact | Likelihood | Mitigation | Owner | Status |
|------|--------|------------|-----------|-------|--------|
| Scope creep UI | Delay core | M | Strict v1 scope doc | PM | Open |
| Security gap (policies) | Trust erosion | M | Stub policies + roadmap transparency | Sec | Open |
| Performance regressions | Latency > target | M | Add perf test harness early | Core | Open |
| Limited contributors | Slow velocity | H | Improve onboarding docs | PM | Open |

## Requirement Set
See `requirements.md` for full details. Traceability matrix links each requirement to artifacts & tests.

## Change Control
Material scope changes require RFC (see `rfcs/`). Update this plan via PR referencing impacted requirement IDs.

## Reporting Cadence
Bi-weekly progress update referencing milestones table & risk changes.

---
**Date:** Aug 2025 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
