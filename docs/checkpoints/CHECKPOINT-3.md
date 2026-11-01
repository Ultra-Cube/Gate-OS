# Checkpoint 3 — Integration Specification

**Status:** Pending maintainer approval  
**Date:** 2026-11-01  
**Branch:** `docs/phase3-integration-spec`

## Completed

- Added `docs/architecture/INTEGRATION.md` with the layered model, interfaces, failure modes, target manifest v2 contract, switch sequence, timing targets, shell strategy, isolation, and data bridge.
- Added `docs/architecture/UPSTREAM.md` with seven environment directions, delivery boundaries, Gate-OS glue, and license/review rules.
- Added both documents to MkDocs navigation.

## Evidence

- Documentation files created and linked in `mkdocs.yml`.
- Existing regression baseline remains 394 passing tests from the previous checkpoint.
- Timing values are explicitly labeled targets; no performance claim was added.

## Remaining work

- Implement and version the manifest v2 schema.
- Verify exact upstream versions, digests, SPDX licenses, and maintenance status.
- Security review must approve runtime isolation, signature enforcement, and bridge policy before release.
- MkDocs strict build remains pending because MkDocs is unavailable in the current environment.

## Decision needed

Approve the integration contract and authorize Phase 4 concept UI work while implementation and security enforcement remain tracked as separate tasks.