# Gate-OS Phase 0 Audit

**Date:** 2026-11-01  
**Branch:** `feat/phase0-audit`  
**Scope:** repository source, tests, manifests, workflows, documentation, release scripts, security surfaces, and license evidence.

## Executive finding

Gate-OS is a credible Python environment-manager prototype with broad test scaffolding and working pieces for manifests, API routing, containers, services, profiles, switching, telemetry, UI logic, signing, packaging, and update staging. It is not yet a verified installable Linux distribution or production-secure environment switcher.

No ISO installation or QEMU/OVMF boot evidence was found in the repository. Security controls such as OIDC verification, container isolation attachment, manifest-signature enforcement, OTA integrity verification, and cryptographic plugin verification are incomplete or advisory.

## Reproducible baseline

- `make test-cov`: **394 passed**.
- Coverage: **94%**, 1,856 statements and 112 missed lines, measured locally with `pytest --cov=gateos_manager --cov-report=term-missing`.
- The first baseline run exposed a timing assumption in `tests/test_telemetry_batch.py`; the test was corrected to assert the actual contract (a remainder remains before the interval) and the suite was rerun successfully.
- CI currently enforces a 70% coverage gate, which is lower than several documentation claims.
- No committed coverage report or verified real-hardware benchmark was found.

## What is implemented

- Manifest YAML loading, schema validation, migration, and digest warnings.
- Podman/Docker runtime detection and lifecycle command construction.
- systemd service lifecycle abstraction.
- CPU governor profile application and switch orchestration with best-effort rollback.
- FastAPI routes, token authentication, WebSocket status, rate limiting, Prometheus, and OTLP integrations.
- Ed25519 signing as standalone functionality.
- Plugin discovery and hook registry.
- GTK/Libadwaita logic and desktop integration adapters, mostly tested with mocks.
- ISO/packaging script structure, AppArmor/seccomp artifacts, and updater staging.
- Shared AI workspace, local read-mostly MCP stubs, and offline Ultra AI contract stub.

## Incomplete, stubbed, or unverified

- OIDC accepts long bearer strings and the optional JWT path disables signature verification.
- `apply_isolation()` emits telemetry but does not attach AppArmor/seccomp, namespace, or read-only-root flags to runtime commands.
- Manifest signatures are not required by the switch path.
- OTA staging does not verify SHA-256 or Ed25519 signatures before marking an update ready.
- Plugin signature checks are not cryptographic and untrusted plugins can load in-process.
- GPU mode, NIC priority, DDE integration, mobile client, read-only root/overlay, and full installer flow are incomplete.
- No physical hardware or QEMU/OVMF installation evidence is committed.

## CI and release findings

- `ci.yml` runs Ruff, validation, markdown/yaml checks, tests, coverage, and Syft/Grype, but the effective gate is 70%.
- `dev-check.sh` makes manifest validation non-blocking and does not run `pip-audit` despite documentation references.
- SBOM/vulnerability outputs are not consistently retained as release artifacts.
- ISO downloads are not checksum-verified and no BIOS/UEFI QEMU job is present.
- `publish.yml` can publish on a tag without the full test/security/release gate.
- Action references and downloaded tools require immutable pinning for a reproducible release.

## Claims versus evidence

| Claim | Evidence | Reality today |
|---|---|---|
| Universal Linux distribution | README product language | Manager prototype and ISO scripts exist; complete distribution/install evidence is absent. |
| Ubuntu 24.04 LTS base | `scripts/build-iso.sh` | Build target is documented; a successful bootable artifact is not evidenced. |
| 198 tests | README badge/text | Current run is 394 passing tests. Existing claims are stale. |
| 90–95% coverage | README/docs | Current local measurement is 94%; CI gate is 70%; publish a reproducible artifact before making a release claim. |
| Production-ready security | README/security prose | OIDC, isolation attachment, signature enforcement, and OTA verification remain incomplete. |
| AppArmor/seccomp enforced | profiles and diagrams | Profiles exist, but the container manager does not attach them. |
| Signed manifests protect switching | signing module | Sign/verify exists; activation does not require verification. |
| Digest-pinned supply chain | loader/docs | Mutable tags remain in examples and digest handling is advisory. |
| OTA updates | updater | Download/staging exists; cryptographic verification is missing. |
| Mobile companion | README | WebSocket API exists; Flutter client is absent. |
| Complete environments | README/examples | Manifests and references exist; distributable app bundles are not proven. |
| Installable ISO | README/build script | Build structure exists; checksum, installer, boot, and installation evidence are absent. |

## License and dependency evidence

Runtime dependencies are PyYAML and jsonschema. Development/API dependencies include pytest, pytest-asyncio, pytest-cov, Ruff, httpx, FastAPI, Uvicorn, Pydantic, watchdog, and coverage-badge. Optional code paths refer to cryptography and JWT libraries without a complete declared/locked dependency policy.

The repository license is GPL-3.0-or-later, but a complete third-party matrix was absent before this audit. Container images, ISO packages, fonts, icons, proprietary clients, Android/GApps components, and sensitive upstream tools require classification before distribution.

See [LICENSES-AND-THIRD-PARTY.md](LICENSES-AND-THIRD-PARTY.md) for the initial review register.

## Prioritized backlog

1. Close authentication and privileged-operation gaps: real JWT/OIDC verification and authenticated token rotation.
2. Enforce manifest signatures and immutable image digests in secure/release modes.
3. Attach AppArmor/seccomp and namespace/read-only settings to container commands.
4. Verify OTA checksums/signatures before staging and verify plugins cryptographically out of process.
5. Make CI validation, SBOM, vulnerability, coverage, and release gates blocking and artifact-producing.
6. Build and QEMU-test the first installable Ubuntu image before updating product claims.
7. Reconcile stale docs, links, service names, test counts, and coverage claims.
8. Raise meaningful coverage toward the 90% target only after security and release paths are tested.

## Phase 0 conclusion

The project is suitable for continued engineering as a manager prototype. It is not suitable for a public v2.0 ISO release claim yet. Phase 1 entry requires security/release owners, a license matrix, a reproducible image pipeline, and a first QEMU installation evidence artifact.
