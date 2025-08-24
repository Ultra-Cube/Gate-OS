<!-- Gate-OS Root README -->
# Gate-OS 🐧

<div align="center">
  
![Gate-OS Logo](https://via.placeholder.com/200x200.png?text=Gate-OS) <!-- Replace with actual logo -->

**The Universal Linux Distribution - One OS for All Environments**  
*Seamlessly switch between gaming, development, design, and media environments*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![CI](https://github.com/Ultra-Cube/Gate-OS/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Coverage](./coverage.svg)](coverage.xml)
[![Dev Check](https://github.com/Ultra-Cube/Gate-OS/actions/workflows/dev-check.yml/badge.svg)](.github/workflows/dev-check.yml)
[![Docs](https://img.shields.io/badge/docs-index-brightgreen.svg)](docs/README.md)
[![Roadmap](https://img.shields.io/badge/status-Phase%202%20In%20Progress-orange.svg)](docs/roadmap/milestones.md)
[![Ultra Cube Tech](https://img.shields.io/badge/by-Ultra%20Cube%20Tech-blue.svg)](https://www.ucubetech.com)

</div>

---

## Quick Links

| Area | Link |
|------|------|
| Documentation Index | [docs/README.md](docs/README.md) |
| Vision & Mission | [docs/business/vision-mission.md](docs/business/vision-mission.md) |
| Architecture Overview | [docs/architecture/overview.md](docs/architecture/overview.md) |
| Roadmap & Milestones | [docs/roadmap/milestones.md](docs/roadmap/milestones.md) |
| Product Features | [docs/product/features.md](docs/product/features.md) |
| Governance | [docs/contribution/governance.md](docs/contribution/governance.md) |
| UI/UX Guidelines | [docs/ui-ux/branding.md](docs/ui-ux/branding.md) |
| Legal & Licensing | [docs/legal/licensing.md](docs/legal/licensing.md) |
| Security Policy | [SECURITY.md](SECURITY.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| Examples Index | [examples/README.md](examples/README.md) |

---

## 🎯 Overview

Gate-OS is a universal Linux distribution that unifies multiple specialized
environments—gaming, development, design, and media—into a single, modular
operating system. Users can seamlessly switch between these environments,
each optimized for its purpose, without needing multiple OS installs.

### Elevator Pitch

Gate-OS turns one workstation into many purpose‑built machines – without reboot rituals,
multi‑boot clutter, or fragile dotfile juggling. Define an "environment" as code
(manifests + container bundle + profile) and switch in seconds. It's the convergence
layer between a traditional Linux distro, a developer platform, and a tuned
workstation appliance.

### Why It Matters

| Problem Today | Gate-OS Solution |
|---------------|------------------|
| Multiple OS installs for gaming/dev/design | Deterministic environment switching on one base install |
| Manual toolchain isolation | Declarative manifests + container encapsulation |
| Context switching overhead | One command / API trigger to pivot workflows |
| Drift & config snowball | Versioned, auditable environment definitions |
| Security friction | Capability allowlists & (future) sandbox/isolation profiles |

### Key Differentiators

- Environment-as-Code (EaC) schema: reproducible switching
- Pluggable orchestration: pre/post/shutdown hooks
- Container runtime abstraction (podman / docker / dry-run)
- Structured telemetry + OTLP export for fleet / ops insight
- Designed for future UI shell integration & remote companion control

### Vision in One Line

One OS install that becomes any workstation you need – instantly, predictably, safely.

### Core Value

- One install, many roles
- Deterministic environment switching
- Modular, enterprise-aligned architecture

### Feature Matrix (Early Phase)

| Capability | Status | Notes |
|------------|--------|-------|
| Manifest schema validation | ✅ | JSON/YAML validated against spec |
| Switch orchestration core | ✅ | Dry-run + container start pipeline |
| Container runtime detection | ✅ | podman → docker → dry-run fallback |
| Plugin hooks (pre/post/shutdown) | ✅ | Python entrypoints registry |
| Telemetry (stdout/file/OTLP) | ✅ | Batch + atexit flush |
| Rate-limited Control API | ✅ | Token auth + headers |
| Capability allowlist (security) | ✅ | Enforced for security domain manifests |
| Isolation enforcement | 🧪 | Stub – profiles upcoming |
| Desktop shell integration | ⏳ | Phase 3 target |
| GUI Switch Panel | ⏳ | Planned after stable API |
| Remote companion app | 🔭 | Concept exploration |
| Signed environment bundles | 🔭 | Supply chain milestone |

Legend: ✅ shipped · 🧪 experimental · ⏳ planned (roadmap) · 🔭 future concept

---

## 🌟 Vision & Mission (Summary)

See full: [docs/business/vision-mission.md](docs/business/vision-mission.md)

| Pillar | Summary |
|--------|---------|
| Unified Experience | Seamless cross-domain workflows |
| Performance | Low-overhead switching & tuned profiles |
| Security & Trust | Isolation + auditable manifests |
| Community | Open governance, extensibility |

---

## 🏗️ Architecture Snapshot

Detailed design: [docs/architecture/overview.md](docs/architecture/overview.md)

```text
Core Kernel / Base
  ├─ Core Services (env registry, policy)
  ├─ Environment Manager (switch orchestration)
  ├─ Container Layer (Docker/Podman)
  ├─ UI Shell (GTK4 / Libadwaita)
  └─ Telemetry & Security (planned)
```

### Layer Deep Dive (Concise)

| Layer | Responsibility | Extensibility |
|-------|----------------|---------------|
| Manifest Schema | Define environment intent | Versioned spec + validation |
| Switch Orchestrator | Coordinates validation → containers → hooks | Plugin lifecycle hooks |
| Container Manager | Abstracts runtime differences & isolation | Additional runtimes (future) |
| Telemetry Emitter | Unified event bus (logs/OTLP/file) | Export adapters (custom) |
| Security Module | Capability policy + isolation stubs | Profiles (seccomp/AppArmor) |
| API Server | Programmatic control & automation | Additional auth backends |

---

## 📚 Documentation Map

High-level index for faster navigation across all knowledge domains.

### Product & Strategy

- Vision & Mission: [docs/business/vision-mission.md](docs/business/vision-mission.md)
- Market Analysis: [docs/business/market-analysis.md](docs/business/market-analysis.md)
- Product Features: [docs/product/features.md](docs/product/features.md)
- Roadmap & Milestones: [docs/roadmap/milestones.md](docs/roadmap/milestones.md)

### Architecture & Engineering

- Overview: [docs/architecture/overview.md](docs/architecture/overview.md)
- Schemas: [docs/architecture/schemas/](docs/architecture/schemas/)
- Control API: [docs/api/control-api.md](docs/api/control-api.md)
- Environment Manifests: [docs/environments/](docs/environments/)
- Security Policy & Capability Allowlist: [docs/security/](docs/security/)
- Diagrams: [docs/diagrams/](docs/diagrams/) (planned)
- Threat Model: [docs/security/threat-model.md](docs/security/threat-model.md)
*- Supply Chain & Integrity: [docs/architecture/supply-chain.md](docs/architecture/supply-chain.md)

### Operations & Processes

- Governance: [docs/contribution/governance.md](docs/contribution/governance.md)
- Contribution Guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Security Disclosure: [SECURITY.md](SECURITY.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

### UI / UX

- Branding & Guidelines: [docs/ui-ux/branding.md](docs/ui-ux/branding.md)
- Desktop Integration (Draft): [docs/ui-ux/desktop-integration.md](docs/ui-ux/desktop-integration.md)

### Examples & Extensions

- Examples Overview: [examples/README.md](examples/README.md)
- Environment Manifests: `examples/environments/*.yaml`
- Sample Plugin: [examples/plugins/sample_plugin.py](examples/plugins/sample_plugin.py)
- Plugin Development: [docs/extensions/plugin-development.md](docs/extensions/plugin-development.md)
- Manifest Authoring: [docs/environments/manifest-authoring.md](docs/environments/manifest-authoring.md)
- Design Environment (Blender + publish workflow): [examples/environments/design.yaml](examples/environments/design.yaml)

### Future / Planned

- RFCs: [rfcs/](rfcs/) (scaffold; add proposal template)
- Telemetry Exporter Guide
- Container Isolation Profiles

---

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

More detail: [docs/product/features.md](docs/product/features.md)

---

## 🔄 Switching Concept (High-Level)

1. Validate target environment manifest
2. Quiesce conflicting services
3. Activate container bundle + apply profile
4. Refresh UI shell context
5. Emit telemetry event

### Cross-Environment Workflow (Design → Media)

Blender (Design) outputs renders automatically showcased in the Media (Kodi) environment:

1. Blender container writes renders to `~/GateOS/work/design/renders`.
2. Export helper (`asset-export` in `examples/environments/design.yaml`) detects new files.
3. Helper triggers Kodi library refresh (planned plugin: `publish_to_kodi`).
4. Media environment (Kodi) surfaces latest assets for demo / review.

Benefit: frictionless creative iteration → showcase loop; no manual copying.

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

### Quick Start (Dry-Run Demo)

```bash
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
GATEOS_API_TOKEN=$(gateos gen-token) gateos api &  # start API
curl -H "x-token: $GATEOS_API_TOKEN" http://localhost:8000/environments
```

Add a sample manifest under `examples/environments/dev.yaml` then perform a switch (placeholder endpoint once implemented):

```bash
curl -X POST -H "x-token: $GATEOS_API_TOKEN" -H 'Content-Type: application/json' \
  -d @examples/environments/dev.yaml http://localhost:8000/switch
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

### Security Model (Foundations)

| Aspect | Current | Planned |
|--------|---------|---------|
| Auth | Static token (env/file) | OIDC / mTLS / per-env scopes |
| Capability Policy | Allowlist validation | Policy bundles + signing |
| Isolation | Logging stub | Seccomp/AppArmor profiles + namespaces |
| Supply Chain | Manual review | Signed manifest + provenance attestation |
| Secrets Handling | Env var pass-through (controlled) | Vault / KMS integration |

Threat model & hardening guidance will ship prior to first beta tag.

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

### Manifest Versioning (Draft)

Manifests optionally declare a top-level `schemaVersion` (currently `"1.0"`).

Behavior:

- If `schemaVersion` present and supported → validated against packaged schema `environment-manifest-v<version>.yaml`.
- If absent → falls back to provided schema path (legacy behavior).
- If unsupported → load fails with a clear error.

Roadmap: multiple concurrent schema versions + upgrade assistant.

### Plugin Discovery

At startup the manager attempts to load Python entry point plugins in group `gateos.plugins`.
Each plugin entry point should resolve to a callable whose import triggers hook registration.

Disable auto discovery: `export GATEOS_DISABLE_ENTRYPOINT_PLUGINS=1`.

Hooks exposed:

- `pre_switch`
- `post_switch`
- `shutdown`

See: `docs/extensions/plugin-development.md` & `examples/plugins/`.

### Telemetry Modes

- Immediate: stdout/file JSON lines
- OTLP Single: each event POSTed individually
- OTLP Batch: queue + size/interval based flush + graceful atexit drain

Future: metrics aggregation, span modeling, structured switch performance stats.

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

Read: [docs/contribution/governance.md](docs/contribution/governance.md)

```bash
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS
./scripts/setup-dev-env.sh
pip install .[dev]  # install manager & dev tooling
gateos validate examples/environments/*.yaml --schema docs/architecture/schemas/environment-manifest.schema.yaml
pytest -q
```

Focus Areas: Core Manager, Environment Manifests, UI Shell, Security Isolation.

### Contribution Workflow (Condensed)

1. Fork & branch: `feature/<topic>`
2. Add/adjust manifest or code + tests
3. Run `ruff`, `pytest` (ensure green)
4. Update `CHANGELOG.md` under Unreleased
5. Open PR (template auto-applies) – include rationale & risk notes
6. Merge on approval + passing CI

### Code Quality Tenets

- Deterministic over clever
- Explicit errors (no silent except unless telemetry)
- Minimal surface by default (opt-in features)
- Observability first (logs + telemetry event)
- No hidden global mutation outside designated managers

### Extensibility: Plugin Hooks

| Hook | Timing | Use Cases |
|------|--------|-----------|
| `pre_switch` | Before container activation | Policy gating, env diff checks |
| `post_switch` | After successful activation | UI refresh, metrics emission |
| `shutdown` | On orchestrator failure or process exit path | Cleanup, persistence |

Register via entry point or dynamic discovery (see `examples/plugins`).

---

## 📄 License

Core licensed under **GPLv3**. See `LICENSE`.

Commercial extensions (future) governed separately.

---

## 🛡️ Trademark & Branding

“Gate-OS” & “Ultra Cube” are trademarks of Ultra Cube Tech. Usage guidance: [docs/legal/licensing.md](docs/legal/licensing.md).

---

## 📞 Contact

Website: <https://www.ucubetech.com>  
Email: <info@ucubetech.com>  
GitHub: <https://github.com/Ultra-Cube>

---



### ✨ One OS to Rule Them All – Gate-OS ✨

---

## 🗺️ Roadmap (Inline Snapshot)

| Quarter | Theme | Highlights |
|---------|-------|-----------|
| Q3 2025 | Core Orchestration | Switch pipeline, telemetry, plugin lifecycle |
| Q4 2025 | Isolation & UI Shell | Seccomp/AppArmor profiles, GTK prototype |
| Q1 2026 | Signed Environments | Manifest signing, supply chain tooling |
| Q2 2026 | Remote Control & Metrics | Companion app, richer observability |

Full detail lives in [docs/roadmap/milestones.md](docs/roadmap/milestones.md) (kept canonical).

## ❓ FAQ (Early)

| Question | Answer |
|----------|--------|
| Is this a full distro today? | Not yet – currently the manager + scaffolding. |
| Do I need Docker installed? | Not for dry‑run; real container mode auto-detects runtime if present. |
| When is beta? | Target after isolation profiles + signed manifest pipeline. |
| How stable are APIs? | Pre‑1.0: breaking changes may occur (tracked in CHANGELOG). |
| Will there be a GUI? | Yes – shell integration is roadmap Phase 3. |

## 🧾 Glossary

| Term | Definition |
|------|------------|
| Environment | Declarative bundle describing a role (tooling + policies). |
| Switch | Operation transitioning active environment context. |
| Manifest | JSON/YAML env definition validated against schema. |
| Capability Allowlist | Security gate restricting privileged ops. |
| Dry-Run Mode | Non-executing simulation of container operations. |
| Hook | Plugin callback executed at lifecycle points. |
| EaC | Environment-as-Code paradigm (like IaC for workstation roles). |

---

If something you expected isn't here (no external wiki), open an issue – gaps are tracked aggressively during pre‑beta.

---

## © Copyright

Copyright (c) 2025 **Ultra Cube Tech**. All rights reserved.

This project is released under the terms of the GPLv3 (see [LICENSE](LICENSE)).

Trademarks and brand assets remain the property of Ultra Cube Tech and may
require additional permission for commercial use.


