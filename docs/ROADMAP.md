# Gate-OS Steel Gate Roadmap

This is the execution roadmap for the approved Steel Gate overhaul. Targets are not achievements until reproducible evidence is linked.

## Phase 0 — Audit and ground truth

- [x] Build shared AI workspace and protocol.
- [x] Measure baseline: 394 passing tests, 94% local coverage.
- [x] Produce claims-vs-reality audit.
- [x] Start third-party license register.
- [x] Prioritize security, release, ISO, docs, and UI backlog.
- [x] Checkpoint 0 approval and backlog sign-off.

## Phase 1 — Installable Gate-OS alpha

Owner: distro-release-engineer. Reviewers: linux-systems-engineer, QA, security, license.

- [x] ADR: Ubuntu LTS, kernel flavor, Wayland session, desktop shell, installer.
- [ ] Reproducible base image with pinned package inputs and layer manifests. Build path now verifies Ubuntu SHA-256 manifest; artifact evidence remains pending.
- [ ] Gate-OS service, environment registry, and Everyday environment.
- [ ] Environment sidebar and minimal switch flow with rollback.
- [ ] Calamares or equivalent installer with safe post-install hooks.
- [ ] Checksum, SBOM, signature, and license gate.
- [ ] QEMU BIOS and UEFI live/install/reboot smoke tests. Workflow and bounded script are ready; WSL has no QEMU/OVMF evidence yet.
- [x] `docs/INSTALL.md` and `docs/BUILDING.md`.
- [ ] Checkpoint 1: `v2.0.0-alpha.1` candidate only after evidence.

## Phase 2 — Identity and documentation

- [x] Honest README rewrite and attribution block.
- [ ] Metadata, issue/PR templates, governance/support docs, and topics.
- [x] MkDocs site links, SEO metadata, and concept labeling.
- [x] License matrix started and linked from the public README.
- [ ] Checkpoint 2: docs build and link validation on a runner with MkDocs installed.

## Phase 3 — Integration specification

- [ ] `docs/architecture/INTEGRATION.md` layered model and failure modes.
- [ ] Manifest v2 schema with licenses, digests, permissions, shell, hooks, and signature.
- [ ] Switch pipeline timing targets labeled as targets.
- [ ] Verified upstream matrix and per-environment shell strategy.
- [ ] Resource isolation and controlled data bridge.
- [ ] Checkpoint 3.

## Phase 4 — Concept UI

- [ ] Design tokens and generated CSS/GTK/QSS.
- [ ] Light/dark/high-contrast LTR/RTL mockups for desktop, sidebar, and seven environments.
- [ ] AI surfaces, installer, first-run, and failure/rollback states.
- [ ] Shell technology ADR and two proof-of-concepts.
- [ ] Playwright-rendered gallery and accessibility review.
- [ ] Checkpoint 4.

## Phase 5 — Optional AI-native layer

- [ ] UI-spec and connector schemas.
- [ ] Native pre-approved renderer and preview/accept/revert flow.
- [ ] Capability tokens, policy gate, audit log, and sandboxed generated web app.
- [ ] Offline mock Ultra AI service and end-to-end demo.
- [ ] Checkpoint 5.

## Phase 6 — Hardening and release

- [ ] Real JWT/OIDC validation and privileged-operation authentication.
- [ ] Enforced manifest signatures and image digest policy.
- [ ] AppArmor/seccomp/runtime isolation attachment.
- [ ] OTA SHA-256/Ed25519 verification and rollback.
- [ ] Cryptographic plugin verification and out-of-process loading.
- [ ] Meaningful coverage target >=90%, measured and published.
- [ ] Signed ISO, SBOM, release notes, upgrade notes, and QEMU evidence.
- [ ] Checkpoint 6: beta release only after security and license approval.

## Working gates

Every task uses a dedicated branch and conventional commit. Existing tests run before and after. New network, dependency, privilege, container, bundled binary, or license surface requires security and license review. The Orchestrator updates this file and writes a checkpoint report; no phase is considered complete from documentation alone.
