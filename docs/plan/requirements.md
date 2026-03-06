# Gate-OS Requirements

## Notation

Each requirement: REQ-<Area>-<Number>. Priority: (M)ust, (S)hould, (C)ould, (W)on't-now.

## Functional Requirements

| ID | Title | Description | Priority | Acceptance Criteria |
|----|-------|-------------|----------|---------------------|
| REQ-MAN-001 | Load Manifest | Load YAML manifest from disk | M | Valid file returns dict <50ms local |
| REQ-MAN-002 | Validate Manifest | Validate against JSON Schema | M | Invalid raises first violation message |
| REQ-MAN-003 | List Environments | CLI lists available manifests | S | `gateos list` prints names & categories |
| REQ-MAN-004 | Switch Environment | Trigger activation flow | M | Exit 0 on success; events emitted |
| REQ-MAN-005 | Hooks Execution | Run pre/post hooks sequentially | S | Hooks logged; failure aborts |
| REQ-SEC-001 | Isolation Level Parse | Parse isolationLevel policy intent | M | strict/balanced/permissive accepted |
| REQ-SEC-002 | Deny Invalid Isolation | Reject unknown isolation levels | M | Error with invalid value |
| REQ-UI-001 | UI List View | Display environments in UI shell | S | Two example envs visible |
| REQ-UI-002 | UI Switch Action | User initiates switch | M | Selecting env triggers activation |
| REQ-OBS-001 | Emit Switch Events | Emit JSON start/end events | M | Contains env, timestamp, status |
| REQ-OBS-002 | Basic Metrics | Derive latency from events | S | Latency printed in debug summary |
| REQ-CI-001 | Lint Enforcement | CI fails on lint errors | M | Lint job non-zero on violations |
| REQ-CI-002 | Test Coverage | 80% line coverage gate | S | Coverage report >= threshold |
| REQ-PKG-001 | Package Build Script | Build distributable artifact | S | Script outputs tar/installer |
| REQ-SEC-TOOLS-001 | Security Tool Env | Provide curated security environment | S | security manifest validates & runs |
| REQ-UI-003 | Alternative Desktop (DDE) | Support Deepin Desktop Environment option | S | Session starts under DDE |
| REQ-MOB-001 | Mobile Companion API | Expose local API for Android app | S | Authenticated switch & status endpoints |
| REQ-SEC-CAPS-001 | Capability Allowlist | Enforce allowlist for security env capabilities | M | Invalid capability rejected |
| REQ-API-001 | Control API Endpoints | Provide REST list/get/switch endpoints | M | Endpoints return 2xx & schema |

## Non-Functional Requirements

| ID | Category | Description | Priority | Metric |
|----|----------|-------------|----------|--------|
| REQ-NFR-PERF-001 | Performance | Manifest validation <150ms | M | Time under test |
| REQ-NFR-PERF-002 | Performance | Switch latency <3s median | M | Telemetry measurement |
| REQ-NFR-REL-001 | Reliability | 99% successful switches | M | <1% failures /500 runs |
| REQ-NFR-SEC-001 | Security | No Critical vulns in pipeline | M | Grype scan result |
| REQ-NFR-OBS-001 | Observability | All switches emit paired events | M | 100% sample coverage |
| REQ-NFR-MAINT-001 | Maintainability | Lint & pre-commit auto-fix basics | S | Pre-commit passes |
| REQ-NFR-DOC-001 | Documentation | Contributor setup <30m | S | Survey + timing |

## Derived / Future Requirements (Backlog)

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| REQ-FUT-SEC-ACL | Policy Engine | Capability allowlist enforcement | C |
| REQ-FUT-GPU-QOS | GPU QoS | Allocate GPU resources per profile | C |
| REQ-FUT-NET-QOS | Network QoS | Traffic shaping per environment | C |
| REQ-FUT-PLUG-API | Plugin API | Extension lifecycle API | S |
| REQ-FUT-ANL-UX | UX Analytics | Opt-in anonymized analytics | W |

## Traceability Matrix (v1.2.0 Complete)

| Requirement | Implementation Artifact | Test(s) | Status |
|---|---|---|---|
| REQ-MAN-001 | `manifest/loader.py` | `test_manifest_loader.py` | Done |
| REQ-MAN-002 | `manifest/schemas/` + `loader.py` | `test_manifest_invalid_*.py` | Done |
| REQ-MAN-003 | `cli.py:cmd_list` | `test_cli.py::test_list` | Done |
| REQ-MAN-004 | `orchestrator.py:switch_environment` | `test_orchestrator.py` | Done |
| REQ-MAN-005 | `plugins/registry.py:invoke` | `test_plugins.py` | Done |
| REQ-SEC-001 | `security/policy.py:parse_isolation_level` | `test_security.py::test_isolation_parse` | Done |
| REQ-SEC-002 | `security/policy.py` | `test_security.py::test_invalid_isolation` | Done |
| REQ-UI-001 | `cli.py:cmd_list` | `test_cli.py::test_list_output` | Done |
| REQ-UI-002 | `cli.py:cmd_switch` | `test_cli.py::test_switch` | Done |
| REQ-OBS-001 | `telemetry/otlp.py` + `orchestrator.py` | `test_otlp.py` | Done |
| REQ-OBS-002 | `telemetry/prometheus.py` | `test_prometheus.py` | Done |
| REQ-CI-001 | `.github/workflows/ci.yml` | CI run (ruff/flake8) | Done |
| REQ-CI-002 | `.github/workflows/ci.yml` (95% gate) | `pytest --cov` (308 tests) | Done |
| REQ-PKG-001 | `pyproject.toml` (hatchling) | CI build step | Done |
| REQ-SEC-TOOLS-001 | `environments/security.yaml` | `test_example_manifests_validate.py` | Done |
| REQ-MOB-001 | `api/websocket.py` | `test_api_websocket.py` | Done |
| REQ-SEC-CAPS-001 | `security/policy.py:enforce_capabilities` | `test_security.py::test_capabilities` | Done |
| REQ-API-001 | `api/control_api.py` | `test_api.py` | Done |
| REQ-FUT-PLUG-API | `plugins/registry.py` | `test_plugins.py` | Done (v1.2.0) |
| REQ-FUT-SEC-ACL | `security/policy.py` | `test_security.py` | Done (v1.2.0) |
| REQ-FUT-NET-QOS | `profiles/hardware.py` (NIC priority) | `test_hardware_profile.py` | Done (v1.2.0) |

Status Legend: **Done** = implemented + tested | **In Progress** = partial | **Planned** = backlog

## Open Questions (Resolved in v1.2.0)

- Activation rollback semantics: **Resolved** — rollback restores prior state atomically (see orchestrator.py)
- Partial hook failure strategy: **Resolved** — required services abort switch; optional services log warning
- Telemetry backend: **Resolved** — OTLP/HTTP JSON exporter; `GATEOS_OTLP_DISABLE=1` for air-gapped

## Remaining Open Questions

- [ ] When to enforce `--require-sig` flag for unsigned manifests?
- [ ] Is GPU profile scope per-container or per-environment?
- [ ] Token rotation: time-based rotation vs. explicit revoke endpoint?

## Update Process

1. Propose change via Issue / RFC referencing requirement IDs.
2. Update this file in same PR.
3. Maintain traceability matrix row for new/changed requirements.

---
**Date:** March 2026 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
