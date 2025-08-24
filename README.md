<!-- Gate-OS Root README -->
# Gate-OS 🐧

<div align="center">
  
![Gate-OS Logo](https://via.placeholder.com/200x200.png?text=Gate-OS) <!-- Replace with actual logo -->

**The Universal Linux Distribution - One OS for All Environments**  
*Seamlessly switch between gaming, development, design, and media environments*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/Ultra-Cube/Gate-OS/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-report-lightgrey.svg)](coverage.xml)
[![Docs](https://img.shields.io/badge/docs-index-brightgreen.svg)](docs/README.md)
[![Roadmap](https://img.shields.io/badge/status-Phase%202%20In%20Progress-orange.svg)](docs/roadmap/milestones.md)
[![Ultra Cube Tech](https://img.shields.io/badge/by-Ultra%20Cube%20Tech-blue.svg)](https://www.ucubetech.com)

</div>

---

## Quick Links

| Area | Link |
|------|------|
| Documentation Index | docs/README.md |
| Vision & Mission | docs/business/vision-mission.md |
| Architecture Overview | docs/architecture/overview.md |
| Roadmap & Milestones | docs/roadmap/milestones.md |
| Product Features | docs/product/features.md |
| Governance | docs/contribution/governance.md |
| UI/UX Guidelines | docs/ui-ux/branding.md |
| Legal & Licensing | docs/legal/licensing.md |

---

## 🎯 Overview

Gate-OS is a universal Linux distribution that unifies multiple specialized
environments—gaming, development, design, and media—into a single, modular
operating system. Users can seamlessly switch between these environments,
each optimized for its purpose, without needing multiple OS installs.

### Core Value

- One install, many roles
- Deterministic environment switching
- Modular, enterprise-aligned architecture

---

## 🌟 Vision & Mission (Summary)

See full: `docs/business/vision-mission.md`

| Pillar | Summary |
|--------|---------|
| Unified Experience | Seamless cross-domain workflows |
| Performance | Low-overhead switching & tuned profiles |
| Security & Trust | Isolation + auditable manifests |
| Community | Open governance, extensibility |

---

## 🏗️ Architecture Snapshot

Detailed design: `docs/architecture/overview.md`

```text
Core Kernel / Base
  ├─ Core Services (env registry, policy)
  ├─ Environment Manager (switch orchestration)
  ├─ Container Layer (Docker/Podman)
  ├─ UI Shell (GTK4 / Libadwaita)
  └─ Telemetry & Security (planned)
```

---

## 🚀 Current Status

Phase 2: Core System Development (≈40%)  
Refer to: `docs/roadmap/milestones.md`

| Phase | Status | Notes |
|-------|--------|-------|
| P1 Planning | ✅ | Complete |
| P2 Core Dev | 🔄 | Manager + UI work |
| P3 Environments | ⏳ | Spec refinement |

---

## 🛠️ Stack

| Layer | Tech |
|-------|------|
| Base | Ubuntu 22.04 LTS (patched) |
| Manager | Python + GTK4 |
| Containers | Docker / Podman |
| UI | GTK4 + Libadwaita |
| Display | Wayland (X11 compat) |

---

## 🧩 Environments (Planned v1)

| Env | Focus | Key Tools |
|-----|-------|-----------|
| Gaming | Performance | Steam, Lutris, Proton |
| Dev | Toolchains | VS Code, Docker, K8s |
| Design | Creative | GIMP, Blender, Krita |
| Media | Production | Kodi, OBS, Resolve |
| Security | Pentest & Diagnostics | Kali toolset, Burp, nmap |

Companion & future: Mobile control app (local network) + optional Deepin Desktop integration.

More detail: `docs/product/features.md`

---

## 🔄 Switching Concept (High-Level)

1. Validate target environment manifest
2. Quiesce conflicting services
3. Activate container bundle + apply profile
4. Refresh UI shell context
5. Emit telemetry event

---

## 🧪 Early KPIs (Draft)

| Metric | Target (v1) |
|--------|-------------|
| Switch Latency | < 3s |
| Crash-Free Activation | > 99% |
| Memory Overhead | < 8% over base |
| Cold Boot to Ready | < 35s |

---

## 📦 Installation

Prerequisites:

- Python 3.10+ (system package: `python3`, `python3-venv`)
- Git
- (Optional) `podman` or `docker` for future container integration

Clone & install (editable) with development and watch extras:

```bash
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[dev,watch]'
```

Extras:

- `dev` – testing, linting, tooling
- `watch` – file watching (hot reload) via `watchdog`

Minimal runtime only:

```bash
pip install -e .
```

Verify CLI is available:

```bash
gateos --help
```

---

## 👨‍💻 Development Setup

Common one-liner after cloning:

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev,watch]'
```

Run linters & tests:

```bash
ruff check .
pytest -q
```

Format code:

```bash
ruff format .
```

Run full coverage:

```bash
pytest --cov=gateos_manager --cov-report=term-missing
```

Update dependencies (if `pyproject.toml` changed):

```bash
pip install -e '.[dev,watch]' --upgrade
```

---

## 🔐 Auth Token & Security Basics

The Control API uses a simple token (temporary dev mechanism):

Generate a token:

```bash
gateos gen-token
```

Use via env var (fast):

```bash
export GATEOS_API_TOKEN="<token>"
```

Or store in file (default permissions 600):

```bash
gateos gen-token > ~/.config/gateos/token
export GATEOS_API_TOKEN_FILE=~/.config/gateos/token
```

Security capability allowlist is enforced for manifests in the `security` category – see `docs/security/capability-policy.md`.

---

## 🛰️ Running the Control API

Basic launch (port 8000):

```bash
GATEOS_API_TOKEN=$(gateos gen-token) gateos api --host 0.0.0.0 --port 8000
```

Enable file watch (auto-reload manifests) & custom rate limit:

```bash
export GATEOS_WATCH=1          # enable watchdog reloads
export GATEOS_RATE_LIMIT=120   # requests/minute
GATEOS_API_TOKEN=$(gateos gen-token) gateos api
```

OpenAPI docs: <http://localhost:8000/docs>

Headers returned include rate limiting: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

Switch example (curl):

```bash
curl -H "x-token: $GATEOS_API_TOKEN" http://localhost:8000/environments
```

---

## 🔍 Observability

Structured JSON logs go to stdout. Add a telemetry file sink:

```bash
export GATEOS_TELEMETRY_FILE=telemetry.log
GATEOS_API_TOKEN=$(gateos gen-token) gateos api
```

Correlation IDs are injected per request and emitted in both logs & telemetry events for traceability.

---

## ⚙️ Key Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `GATEOS_API_TOKEN` | Direct token auth | `export GATEOS_API_TOKEN=abc123` |
| `GATEOS_API_TOKEN_FILE` | Path to token file | `~/.config/gateos/token` |
| `GATEOS_RATE_LIMIT` | Requests/min (integer) | `120` |
| `GATEOS_WATCH` | Enable manifest watch reload | `1` |
| `GATEOS_TELEMETRY_FILE` | Append telemetry JSON lines | `telemetry.log` |
| `GATEOS_TELEMETRY_OTLP_HTTP` | Send each event to OTLP HTTP endpoint | `http://localhost:4318/v1/traces` |
| `GATEOS_CONTAINER_DRY_RUN` | Avoid real runtime, in-memory state | `1` |
| `GATEOS_CONTAINER_RUNTIME` | Override container runtime binary | `podman` |
| `GATEOS_SECURITY_ENFORCE` | Enable isolation hook stubs | `1` |
| `GATEOS_SECURITY_PROFILE` | Named isolation profile (future) | `strict` |
| `GATEOS_TELEMETRY_BATCH` | Enable OTLP batch mode | `1` |
| `GATEOS_TELEMETRY_BATCH_INTERVAL` | Batch flush interval seconds | `2` |
| `GATEOS_TELEMETRY_BATCH_SIZE` | Max events per batch POST | `50` |

---

## 🤝 Contributing

Read: `docs/contribution/governance.md`

```bash
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS
./scripts/setup-dev-env.sh
pip install .[dev]  # install manager & dev tooling
gateos validate examples/environments/*.yaml --schema docs/architecture/schemas/environment-manifest.schema.yaml
pytest -q
```

Focus Areas: Core Manager, Environment Manifests, UI Shell, Security Isolation.

---

## 📄 License

Core licensed under **GPLv3**. See `LICENSE`.

Commercial extensions (future) governed separately.

---

## 🛡️ Trademark & Branding

“Gate-OS” & “Ultra Cube” are trademarks of Ultra Cube Tech. Usage guidance: `docs/legal/licensing.md`.

---

## 📞 Contact

Website: <https://www.ucubetech.com>  
Email: <info@ucubetech.com>  
GitHub: <https://github.com/Ultra-Cube>

---



### ✨ One OS to Rule Them All – Gate-OS ✨


