# Gate-OS

> **One OS · All Environments** — Switch between development, gaming, design, media, and security profiles instantly.

[![Version](https://img.shields.io/badge/version-1.0.0--beta-orange)](https://github.com/Ultra-Cube/Gate-OS/releases/tag/v1.0.0-beta)
[![Tests](https://img.shields.io/badge/tests-198%20passing-brightgreen)](https://github.com/Ultra-Cube/Gate-OS)
[![License](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/Ultra-Cube/Gate-OS/blob/main/LICENSE)

---

## What is Gate-OS?

Gate-OS is an intelligent Linux environment manager that lets you switch between fully isolated OS profiles — each with its own services, container stack, kernel tuning, AppArmor policy, and resource allocation — in seconds.

Think of it as a **context-switch for your entire operating system**.

```
gateos switch gaming     # Stop dev containers, apply gaming profile, boost GPU
gateos switch dev        # Restore dev environment, start Docker stack
gateos switch security   # Enable Kali tools, strict seccomp, isolated network
```

---

## Features

| Category | Capability |
|----------|-----------|
| **Switching** | Systemd service orchestration, container lifecycle, kernel profiles |
| **Security** | AppArmor per-environment, seccomp profiles, manifest Ed25519 signing |
| **Observability** | Prometheus `/metrics`, Prometheus P99 latency, OTLP/HTTP tracing |
| **Mobile** | WebSocket real-time status, REST remote switch |
| **OTA** | GitHub Releases feed, package download + verify, systemd boot apply |
| **UI** | GTK4 Adwaita desktop panel, system tray icon |
| **ISO** | Ubuntu 24.04 LTS bootable ISO builder, `.deb` overlay installer |

---

## Quick Start

=== "Option A — Full OS ISO"

    ```bash
    # Build the ISO (requires ~10 GB free space and Docker/podman)
    sudo ./scripts/build-iso.sh

    # Flash to USB
    sudo dd if=dist/gate-os-*.iso of=/dev/sdX bs=4M status=progress
    ```

=== "Option B — .deb Overlay"

    ```bash
    # On Ubuntu 24.04 LTS
    sudo dpkg -i gateos-manager_1.0.0-beta_amd64.deb
    sudo systemctl enable --now gateos-api
    ```

=== "Option C — Developer Install"

    ```bash
    git clone https://github.com/Ultra-Cube/Gate-OS.git
    cd Gate-OS
    make setup    # creates .venv, installs all deps
    make test     # runs 198 tests
    make api      # starts the control API on :8088
    ```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Gate-OS Manager                     │
├──────────────┬──────────────────┬───────────────────────┤
│  GTK4 UI     │  Control API     │  WebSocket /ws/status │
│  (Adwaita)   │  FastAPI :8088   │  Mobile Companion     │
├──────────────┴──────────────────┴───────────────────────┤
│              Switch Orchestrator                        │
│  pre_switch → services → profile → containers → post   │
├────────────┬────────────────┬───────────────────────────┤
│ SystemdMgr │ ContainerMgr   │ ProfileApplicator         │
│ (services) │ (podman/docker)│ (CPU gov / GPU / NIC)     │
├────────────┴────────────────┴───────────────────────────┤
│              Security Layer                             │
│  AppArmor profiles · seccomp JSON · Ed25519 signing     │
└─────────────────────────────────────────────────────────┘
```

---

## Project Status

| Phase | Version | Tests | Status |
|-------|---------|-------|--------|
| Foundation | v0.0.4 | 43 | ✅ |
| Dev Env Fix | v0.0.5 | 64 | ✅ |
| Real Switch Engine | v0.0.6 | 68 | ✅ |
| GTK4 UI Shell | v0.1.0 | 100 | ✅ |
| ISO Builder | v0.2.0 | 114 | ✅ |
| Security Hardening | v0.3.0 | 147 | ✅ |
| Observability | v0.4.0 | 166 | ✅ |
| Mobile Companion | v0.5.0 | 178 | ✅ |
| **Beta Release** | **v1.0.0-beta** | **198** | **✅** |
| v1.0 Launch | v1.0.0 | — | 📋 Q4 2026 |

---

## License

Gate-OS is licensed under the [GNU General Public License v3.0](https://github.com/Ultra-Cube/Gate-OS/blob/main/LICENSE).
