---
name: security-env-terminal-ui
description: "Use when building or evaluating the Security environment terminal-first UI and isolated offensive-security tools."
---

## Procedure
Use a maintained, reviewed shell; isolate tools in hardened network-scoped containers; require explicit consent for offensive actions; define capability and audit policies; test against known historical vulnerabilities.

## Pitfalls
Using archived eDEX-UI without review, exposing host sockets, unrestricted network access, and presenting offensive tools without safety boundaries.

## Verification
AppArmor/seccomp evidence, network policy tests, tool provenance, explicit consent flow, and clean teardown.
