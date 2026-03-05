---
title: Roadmap & Milestones
project: Gate-OS
owner: Ultra Cube Tech
status: Active
last-updated: 2026-03-05
---

# Gate-OS — Roadmap & Milestones

> Ultra Cube Tech — Structured delivery path.  
> Last updated: **March 5, 2026** | Current release: **v1.1.0** | Next: **v1.2.0**

---

## Delivery Phases Overview

| Phase | Title | Version | Status |
|-------|-------|---------|--------|
| Phase 0 | Foundation & Scaffold | v0.0.4 | ✅ Complete |
| Phase 1 | Dev Environment Fix | v0.0.5 | ✅ Complete |
| Phase 2 | Real Switch Engine | v0.0.6 | ✅ Complete |
| Phase 3 | GTK4 UI Shell | v0.1.0 | ✅ Complete |
| Phase 4 | Ubuntu ISO Builder | v0.2.0 | ✅ Complete |
| Phase 5 | Security Hardening | v0.3.0 | ✅ Complete |
| Phase 6 | Performance & Observability | v0.4.0 | ✅ Complete |
| Phase 7 | Mobile Companion (WebSocket) | v0.5.0 | ✅ Complete |
| Phase 8 | Beta Release | v1.0.0-beta | ✅ Complete |
| Phase 9 | Quality & Observability | v1.1.0 | ✅ Complete |
| Phase 10 | Coverage Sprint | v1.2.0 | ⏳ Q2 2026 |
| Phase 11 | Documentation & Diagrams | v1.2.0 | ⏳ Q2 2026 |
| Phase 12 | Profile & System Completion | v1.3.0 | 📋 Q3 2026 |
| Phase 13 | Security Hardening v2 | v1.3.0 | 📋 Q3 2026 |
| Phase 14 | Flutter Mobile App | v1.4.0 | 📋 Q3-Q4 2026 |
| Phase 15 | v1.0.0 Stable Launch | v1.0.0 | 📋 Q4 2026 |

---

## Milestone Detail Table

| ID | Milestone | Phase | Target | Status |
|----|-----------|-------|--------|--------|
| M1 | Architecture & specs defined | 0 | 2025-08 | ✅ Done |
| M2 | Manifest schema v0.1.0 + examples | 0 | 2025-08 | ✅ Done |
| M3 | Switch orchestrator skeleton | 0 | 2025-08 | ✅ Done |
| M4 | Telemetry stub (batch OTLP queue) | 0 | 2025-08 | ✅ Done |
| M5 | FastAPI Control API + auth | 0 | 2025-08 | ✅ Done |
| M6 | Dev toolchain fix (pip/pytest/Makefile) | 1 | 2026-03 | ✅ Done |
| M7 | ServiceManager (systemd) | 2 | 2026-03 | ✅ Done |
| M8 | ContainerManager real podman (timeout/labels/volumes) | 2 | 2026-03 | ✅ Done |
| M9 | Performance benchmark test harness | 2 | 2026-03 | ✅ Done |
| M10 | GTK4 UI shell (env list + switch + tray) | 3 | 2026-03 | ✅ Done |
| M11 | Ubuntu 24.04 ISO builder script | 4 | 2026-03 | ✅ Done |
| M12 | AppArmor + seccomp profiles (5 envs) | 5 | 2026-03 | ✅ Done |
| M13 | Manifest signing CLI (Ed25519) | 5 | 2026-03 | ✅ Done |
| M14 | Prometheus /metrics endpoint | 6 | 2026-03 | ✅ Done |
| M15 | WebSocket /ws/status endpoint | 7 | 2026-03 | ✅ Done |
| M16 | OTA updater (check + apply via systemd) | 8/9 | 2026-03 | ✅ Done |
| M17 | Real OTLP/HTTP JSON exporter | 9 | 2026-03 | ✅ Done |
| M18 | MkDocs Material docs scaffold | 9 | 2026-03 | ✅ Done |
| M19 | Test coverage ≥ 87% | 9 | 2026-03 | ✅ Done |
| M20 | Coverage ≥ 90% (all modules) | 10 | Q2 2026 | ⏳ Next |
| M21 | Architecture diagrams (Mermaid) | 11 | Q2 2026 | ⏳ Next |
| M22 | Docs site live on GitHub Pages | 11 | Q2 2026 | ⏳ Next |
| M23 | GPU/NIC real profile application | 12 | Q3 2026 | 📋 Planned |
| M24 | allowlistRef + network namespace in schema | 12 | Q3 2026 | 📋 Planned |
| M25 | API token rotation + OIDC stub | 13 | Q3 2026 | 📋 Planned |
| M26 | Plugin sandbox + signature verification | 13 | Q3 2026 | 📋 Planned |
| M27 | Flutter Android app MVP | 14 | Q3 2026 | 📋 Planned |
| M28 | FCM push notifications | 14 | Q4 2026 | 📋 Planned |
| M29 | v1.0.0 Stable release + enterprise pilot | 15 | Q4 2026 | 📋 Planned |

---

## KPIs

| KPI | Target | Current State |
|-----|--------|---------------|
| Switch latency | < 3s median | ✅ < 50ms dry-run (real HW TBD) |
| Environment activation reliability | > 99% | ⏳ Not measured in production |
| Test line coverage | ≥ 90% | 87% (v1.1.0) |
| Critical vulnerabilities | 0 High/Critical | ✅ pip-audit clean |
| Community contributors | 25 (Year 1) | ⏳ In progress |
| Enterprise pilots | 2 (Year 1) | 📋 Planned Q4 2026 |
| Docs site live | GitHub Pages | ⏳ Scaffold ready, deploy pending |

---

## Review Cadence

- Monthly roadmap sync (PM + Core Dev)
- Quarterly strategic review (Ultra Cube Tech leadership)
- Coverage audit after every sprint

---

**Date:** March 2026 | **By:** Fadhel.SH  
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/) | [LinkedIn](https://www.linkedin.com/company/ultra-cube)
