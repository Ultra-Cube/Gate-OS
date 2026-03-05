---
title: Architecture Overview
project: Gate-OS
owner: Ultra Cube Tech
status: Active
last-updated: 2026-03-05
---

# Architecture Overview

> Ultra Cube Tech — Foundation of the multi-environment OS.  
> Current version: **v1.1.0** | 228 tests passing | 87% coverage

---

## System Layers

```mermaid
graph TD
    subgraph "Hardware"
        HW[CPU / GPU / NIC / Storage]
    end

    subgraph "Kernel & Base OS"
        K[Ubuntu 24.04 LTS Kernel]
        PF[CPU Governor / cpufreq sysfs]
        GPU[GPU Mode — nvidia-smi / AMD sysfs ⏳]
        NIC[NIC QoS — tc/qdisc ⏳]
    end

    subgraph "Core Services"
        SM[ServiceManager — systemd start/stop]
        CM[ContainerManager — podman/docker]
        AA[AppArmor Loader — load-apparmor-profiles.sh]
    end

    subgraph "Gate-OS Manager"
        ML[ManifestLoader — JSON Schema v0.1.0]
        SO[SwitchOrchestrator — activation lifecycle]
        PA[ProfileApplicator — CPU / GPU / NIC]
        UPD[OTA Updater — dpkg + systemd drop-in]
    end

    subgraph "API Layer"
        API[FastAPI Control API :8088]
        WS[WebSocket /ws/status]
        RL[RateLimiter + TokenAuth]
        PR[Prometheus /metrics]
    end

    subgraph "Telemetry"
        TE[TelemetryEmitter — batch queue]
        OT[OTLPExporter — HTTP/JSON spans+logs]
        PM2[PrometheusRegistry — counters/gauges/histograms]
    end

    subgraph "UI Shell"
        APP[GateOSApp — Adw.Application]
        ENV[EnvListPanel — Adw.PreferencesGroup]
        SB2[StatusBar — live API health]
        TR[AppIndicatorTray — system tray]
    end

    subgraph "Security"
        SGN[ManifestSigning — Ed25519]
        AAP[AppArmor Profiles — 5 environments]
        SCP[seccomp Profiles — OCI + strict]
        PLG[PluginRegistry — pre/post/shutdown hooks]
    end

    HW --> K
    K --> PF & GPU & NIC
    PF & GPU & NIC --> PA
    PA --> SO
    SM --> SO
    CM --> SO
    ML --> SO
    SO --> API
    API --> WS & RL & PR
    SO --> TE
    TE --> OT & PM2
    API --> APP
    APP --> ENV & SB2 & TR
    SGN & AAP & SCP --> SO
    PLG --> SO
```

---

## Logical Layers

| Layer | Responsibility | Implementation |
|-------|----------------|----------------|
| Kernel/Base | Performance, hardware drivers | Ubuntu 24.04 LTS + cpufreq sysfs |
| Core Services | systemd orchestration, container lifecycle | `ServiceManager`, `ContainerManager` |
| Env Manager | Switch lifecycle, manifest validation, rollback | `SwitchOrchestrator`, `ManifestLoader` |
| Profile Application | CPU governor, GPU mode, NIC priority | `ProfileApplicator` |
| Security | AppArmor/seccomp enforcement, manifest signing | `signing.py`, `profiles/` |
| Control API | REST + WebSocket; auth, rate limiting | FastAPI + `api/server.py`, `api/websocket.py` |
| Telemetry | Structured events, Prometheus metrics, OTLP | `telemetry/emitter.py`, `telemetry/otlp.py` |
| UI Shell | GTK4/Libadwaita desktop panel + system tray | `ui/app.py`, `ui/tray.py` |
| Plugin System | Pre/post/shutdown extension hooks | `plugins/registry.py` |
| OTA Updater | Version check, dpkg apply, systemd drop-in | `updater.py` |

---

## Technical Stack

| Component | Technology | Status |
|-----------|-----------|--------|
| Language | Python 3.12 | ✅ Active |
| Base OS | Ubuntu 24.04 LTS | ✅ Confirmed |
| UI Toolkit | GTK4 + Libadwaita (PyGObject ≥ 3.44) | ✅ Implemented |
| Container Runtime | Podman (+ Docker fallback) | ✅ Real orchestration |
| Init System | systemd (units + drop-ins) | ✅ Active |
| Control API | FastAPI + uvicorn | ✅ Implemented |
| Telemetry | OTLP/HTTP JSON (custom, no SDK) + Prometheus | ✅ Implemented |
| Security | AppArmor (5 profiles) + seccomp (2 configs) + Ed25519 signing | ✅ Implemented |
| Packaging | `.deb` build + preseed generator | ✅ Implemented |
| ISO Build | `scripts/build-iso.sh` (xorriso + squashfs) | ✅ Implemented |
| Docs | MkDocs Material + GitHub Pages | ⏳ Deploy pending |
| Mobile | WebSocket API ready; Flutter app | ⏳ Planned Phase 14 |

---

## Environment Switching Flow

```mermaid
sequenceDiagram
    participant U as User / Mobile App
    participant API as FastAPI :8088
    participant SO as SwitchOrchestrator
    participant ML as ManifestLoader
    participant SM as ServiceManager
    participant PA as ProfileApplicator
    participant CM as ContainerManager
    participant TE as TelemetryEmitter
    participant WS as WebSocket /ws/status

    U->>API: POST /switch/{env}
    API->>WS: broadcast switch_start
    API->>SO: activate(env)
    SO->>ML: load_manifest(env)
    ML-->>SO: manifest dict
    SO->>TE: emit(switch_start)
    SO->>PLG: run pre_switch hooks
    SO->>SM: stop_services(old_manifest)
    SO->>PA: apply(manifest.profile)
    SO->>CM: start_containers(manifest.containers)
    CM-->>SO: container IDs
    SO->>SM: start_services(manifest)
    SO->>PLG: run post_switch hooks
    SO->>TE: emit(switch_done, latency)
    API->>WS: broadcast switch_done
    API-->>U: 200 OK {status, latency_ms}
```

---

## Module Dependency Map

See [docs/diagrams/](../diagrams/) for Mermaid diagram files.

Key dependencies:
- `switch/orchestrator.py` → `manifest/loader.py`, `containers/manager.py`, `services/__init__.py`, `profile/__init__.py`, `plugins/registry.py`, `telemetry/emitter.py`
- `api/server.py` → `switch/orchestrator.py`, `telemetry/prometheus.py`, `api/auth.py`, `api/rate_limit.py`
- `ui/app.py` → `ui/api_client.py`, `ui/env_list.py`, `ui/switch_button.py`, `ui/status_bar.py`, `ui/tray.py`
- `updater.py` → `telemetry/emitter.py`
- `telemetry/otlp.py` → (no internal deps, stdlib only)

---

## Configuration Strategy

- Declarative JSON manifests per environment (`data/environments/*.json`)
- Versioned JSON Schema v0.1.0 with migration hooks (`manifest/loader.py`)
- Schema: `docs/architecture/schemas/environment-manifest.schema.yaml`
- All runtime tunables via env vars (`GATEOS_*` prefix)

---

## Security Architecture

| Threat Surface | Current Control | Planned Enhancement |
|----------------|-----------------|---------------------|
| API Token | Static random token (env var) | Rotating token + OIDC stub (Phase 13) |
| Plugin Execution | Import + run (trusted) | Signature + process sandbox (Phase 13) |
| Manifests | JSON Schema + Ed25519 verification | allowlistRef policy engine (Phase 12) |
| Containers | AppArmor + seccomp per env | Digest pinning + network namespace (Phase 12/13) |
| Telemetry Transport | Plain HTTP OTLP | TLS + PII redaction (Phase 13) |
| Supply Chain | Syft SBOM + Grype scan (CI) | SLSA provenance attestation (Phase 13) |

---

## Open Items (Tracked)

| Item | Phase | Status |
|------|-------|--------|
| GPU real implementation (nvidia-smi / AMD sysfs) | 12 | ⏳ Planned |
| NIC priority via tc/qdisc | 12 | ⏳ Planned |
| Network namespace per container | 12 | ⏳ Planned |
| Architecture diagram files in docs/diagrams/ | 11 | ⏳ Next sprint |
| DDE shell adapter interface | 12 | ⏳ Planned |

---

**Date:** March 2026 | **By:** Fadhel.SH  
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/) | [LinkedIn](https://www.linkedin.com/company/ultra-cube)
