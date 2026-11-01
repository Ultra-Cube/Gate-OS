---
name: release-signing-and-ota
description: "Use when preparing signed Gate-OS ISOs, checksums, SBOMs, manifests, release notes, or OTA channels."
---

## Procedure
Build from reviewed inputs; generate SBOM and checksums; sign with protected keys; publish verification instructions; enforce signed manifest and rollback in OTA clients; never log private material.

## Verification
Detached signatures verify from a clean machine, provenance is recorded, upgrade/downgrade policy is tested, and release checklist is complete.
