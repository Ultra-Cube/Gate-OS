# System Architecture Diagram

> Gate-OS layered component overview — C4 Container level.

```mermaid
graph TB
    subgraph "Mobile Companion (Phase 14)"
        FL[Flutter Android App]
    end

    subgraph "UI Shell — GTK4 / Libadwaita"
        APP[GateOSApp\nAdw.Application]
        ENVL[EnvListPanel\nAdw.PreferencesGroup]
        SWB[SwitchButton\nGtk.Spinner + badge]
        SBAR[StatusBar\n5s auto-poll]
        TRAY[AppIndicatorTray\nsystem tray icon]
    end

    subgraph "Gate-OS Control API — FastAPI :8088"
        AUTH[TokenAuth\nstatic bearer token]
        RL[RateLimiter\nIn-memory sliding window]
        REST[REST Endpoints\n/environments /switch/{env}]
        WS[WebSocket\n/ws/status broadcast]
        MET[Prometheus\n/metrics text/plain]
    end

    subgraph "Gate-OS Manager Core"
        SO[SwitchOrchestrator\nactivation lifecycle + rollback]
        ML[ManifestLoader\nJSON Schema v0.1.0 validation]
        PLG[PluginRegistry\npre_switch / post_switch / shutdown]
        UPD[OTA Updater\ncheck + schedule_apply systemd]
    end

    subgraph "Hardware Abstraction"
        SM[ServiceManager\nsystemctl start/stop/status]
        CM[ContainerManager\npodman run/stop/rm + labels]
        PA[ProfileApplicator\ncpufreq governor + GPU⏳ + NIC⏳]
    end

    subgraph "Security"
        SGN[ManifestSigning\nEd25519 sign/verify]
        AAP[AppArmor Profiles\n5 environments enforce/complain]
        SCP[seccomp Profiles\nOCI + strict]
    end

    subgraph "Telemetry"
        TE[TelemetryEmitter\nstructured JSON + batch queue]
        OTLP[OTLPExporter\nHTTP/JSON spans + logs]
        PROM[PrometheusRegistry\nCounter/Gauge/Histogram]
    end

    subgraph "Storage"
        MAN[Environment Manifests\ndata/environments/*.json]
        SCHEMA[JSON Schema\nv0.1.0]
        FLAGS[Update Flag Files\n/var/lib/gateos/]
    end

    FL -->|WebSocket ws://| WS
    FL -->|REST http://| REST
    APP --> ENVL & SWB & SBAR & TRAY
    APP -->|HTTP| REST
    SBAR -->|HTTP poll| REST
    REST --> AUTH --> RL --> SO
    WS -->|broadcast| FL & APP
    SO --> ML --> SCHEMA
    ML --> MAN
    SO --> PLG
    SO --> SM & PA & CM
    SO --> TE
    TE --> OTLP & PROM
    MET --> PROM
    SO --> SGN
    CM --> AAP & SCP
    UPD --> FLAGS
    UPD --> SM
```

## Layer Descriptions

| Layer | Components | Notes |
|-------|-----------|-------|
| Mobile | Flutter app (Phase 14) | WebSocket client + REST switch |
| UI Shell | GTK4/Adwaita panel + tray | Headless-safe (CI mode) |
| Control API | FastAPI :8088 | Token auth, rate limit, Prometheus |
| Manager Core | Orchestrator + Loader + Plugins | Rollback on failure |
| Hardware Abstraction | systemd, podman, cpufreq | Real OS-level control |
| Security | AppArmor/seccomp + Ed25519 | All 5 environments profiled |
| Telemetry | OTLP + Prometheus | No external SDK; stdlib only |
| Storage | JSON manifests + schema | Schema v0.1.0 versioned |

---
**Last updated:** March 2026 | **By:** Fadhel.SH
