# System Architecture Diagram

> Gate-OS layered component overview — C4 Container level.

```mermaid
graph TB
    subgraph "Mobile Companion (Phase 14)"
        FL[Flutter Android App]
    end

    subgraph "UI Shell — GTK4 / Libadwaita"
        APP["GateOSApp<br/>Adw.Application"]
        ENVL["EnvListPanel<br/>Adw.PreferencesGroup"]
        SWB["SwitchButton<br/>Gtk.Spinner + badge"]
        SBAR["StatusBar<br/>5s auto-poll"]
        TRAY["AppIndicatorTray<br/>system tray icon"]
    end

    subgraph "Gate-OS Control API — FastAPI :8088"
        AUTH["TokenAuth<br/>static bearer token"]
        RL["RateLimiter<br/>In-memory sliding window"]
        REST["REST Endpoints<br/>/environments /switch/{env}"]
        WS["WebSocket<br/>/ws/status broadcast"]
        MET["Prometheus<br/>/metrics text/plain"]
    end

    subgraph "Gate-OS Manager Core"
        SO["SwitchOrchestrator<br/>activation lifecycle + rollback"]
        ML["ManifestLoader<br/>JSON Schema v0.1.0 validation"]
        PLG["PluginRegistry<br/>pre_switch / post_switch / shutdown"]
        UPD["OTA Updater<br/>check + schedule_apply systemd"]
    end

    subgraph "Hardware Abstraction"
        SM["ServiceManager<br/>systemctl start/stop/status"]
        CM["ContainerManager<br/>podman run/stop/rm + labels"]
        PA["ProfileApplicator<br/>cpufreq governor + GPU⏳ + NIC⏳"]
    end

    subgraph "Security"
        SGN["ManifestSigning<br/>Ed25519 sign/verify"]
        AAP["AppArmor Profiles<br/>5 environments enforce/complain"]
        SCP["seccomp Profiles<br/>OCI + strict"]
    end

    subgraph "Telemetry"
        TE["TelemetryEmitter<br/>structured JSON + batch queue"]
        OTLP["OTLPExporter<br/>HTTP/JSON spans + logs"]
        PROM["PrometheusRegistry<br/>Counter/Gauge/Histogram"]
    end

    subgraph "Storage"
        MAN["Environment Manifests<br/>data/environments/*.json"]
        SCHEMA["JSON Schema<br/>v0.1.0"]
        FLAGS["Update Flag Files<br/>/var/lib/gateos/"]
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
