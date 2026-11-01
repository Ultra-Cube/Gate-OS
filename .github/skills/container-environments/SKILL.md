---
name: container-environments
description: "Use when designing Gate-OS OCI environment images, rootless Podman runtimes, cgroup limits, GPU access, SBOMs, or image pinning."
---

## Procedure
Create minimal rootless images; pin immutable digests; declare resources, capabilities, mounts, network, and license metadata; generate SBOM; scan; test start/stop/rollback.

## Pitfalls
Mutable tags, privileged containers, host socket exposure, unbounded resources, secret-bearing layers, and unsupported GPU assumptions.

## Verification
Podman/Docker dry-run and runtime tests, digest enforcement, SBOM/scanner output, least-privilege review, and manifest validation.
