# Checkpoint 0 — Audit and Ground Truth

**Status:** Pending maintainer approval  
**Date:** 2026-11-01  
**Branch:** `feat/phase0-audit`

## Completed

- Audited source packages, tests, manifests, workflows, scripts, packaging, security artifacts, documentation, and the AI workspace.
- Measured the current baseline with `make test-cov`: **394 passed**, **94% coverage** (1,856 statements, 112 missed lines).
- Corrected a timing assumption in `tests/test_telemetry_batch.py`; the test now validates the actual batch contract and passes consistently.
- Added `docs/AUDIT.md` with implemented/stubbed behavior, CI/release findings, security findings, dependency/license gaps, claims-vs-reality table, and prioritized backlog.
- Added `docs/ROADMAP.md` with phases, owners, gates, and checkpoint requirements.
- Added `docs/LICENSES-AND-THIRD-PARTY.md` with the required FOSS-bundled, FOSS-optional, and proprietary-user-downloaded classifications.

## Evidence

- `make test-cov`: 394 passed, 94% local coverage.
- Focused telemetry test: 2 passed.
- JSON/front matter/MCP validations from Checkpoint A remain passing.

## Critical findings

1. OIDC/JWT validation is not cryptographic or complete.
2. Privileged token rotation is available when authentication is disabled.
3. Container isolation artifacts are not attached to runtime commands.
4. Manifest signatures and image digests are not enforced during activation.
5. OTA staging lacks SHA-256/Ed25519 verification.
6. CI/release gates and documentation claims are inconsistent.
7. ISO build and QEMU/OVMF installation evidence is absent.

## Plan changes

Phase 1 must begin with ADRs for the Ubuntu base, shell/session, installer, image inputs, and license boundary. Security fixes and release reproducibility remain gates for an alpha ISO. The 94% figure is a local baseline, not a release claim; coverage must remain meaningful and be published from CI.

## Decision needed

Approve the Phase 0 findings and authorize Phase 1 implementation of the first installable Gate-OS alpha, with security and license review gates preserved.
