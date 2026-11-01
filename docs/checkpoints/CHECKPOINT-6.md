# Checkpoint 6 — Security Hardening Baseline

**Status:** Pending maintainer approval; release gates remain open  
**Date:** 2026-11-01  
**Branch:** `feat/phase6-security-hardening`

## Completed

- Replaced syntactic OIDC acceptance with fail-closed JWT validation against configured JWKS, issuer, audience, expiry, and signature.
- Prevented static-token anonymous fallback when OIDC mode is enabled.
- Required configured authentication for `/auth/rotate-token`.
- Added secure-mode digest enforcement through `GATEOS_REQUIRE_DIGESTS=1` or the loader parameter.
- Added regression tests for unsigned OIDC tokens, anonymous token rotation rejection, and mutable image rejection.
- Added `python-jose[cryptography]` as a declared runtime dependency and recorded it for license review.

## Evidence

- Focused security/manifest tests: 29 passed.
- Full suite: **398 passed**.
- Coverage remains measured at 94% from the previous full coverage run; a new coverage run is required before release claims.

## Remaining release blockers

- Wire manifest signature verification into activation.
- Attach AppArmor/seccomp, namespace, read-only-root, and network policy flags to runtime commands.
- Verify OTA SHA-256 and Ed25519 before staging.
- Replace plugin signature presence checks with cryptographic verification and isolate untrusted loading.
- Complete ISO build, SBOM, signatures, QEMU, and fresh VM installation evidence.
- Run MkDocs/Playwright/QEMU in CI or a Linux VM.

## Decision needed

Approve this security baseline and keep the release channel closed until all remaining blockers have evidence and security/license approval.
