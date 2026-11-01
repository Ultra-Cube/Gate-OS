---
applyTo: "examples/environments/**,**/*manifest*.yaml,**/*manifest*.yml,docs/architecture/schemas/**"
description: "Environment manifest schema, signing, and supply-chain rules"
---

Validate manifests against the versioned schema. Require stable identifiers, explicit runtime and permissions, resource limits, license metadata, image digests, and rollback behavior. Never trust mutable tags in release manifests. Verify signatures before activation and reject unknown capabilities. Add fixtures for malformed, unsigned, expired, and digest-mismatched manifests.
