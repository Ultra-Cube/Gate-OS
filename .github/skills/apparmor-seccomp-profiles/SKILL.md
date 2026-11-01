---
name: apparmor-seccomp-profiles
description: "Use when creating or reviewing AppArmor profiles, seccomp filters, or container syscall and filesystem restrictions."
---

## Procedure
Map capabilities and data flows; begin with complain/audit evidence; write narrow rules; test expected and denied operations; promote to enforce; record exceptions and update policy tests.

## Pitfalls
Broad glob permissions, hidden writes, profile bypass through helpers, and enforcing before collecting legitimate behavior.

## Verification
`aa-status`, audit logs, negative tests, container runtime checks, and documented recovery path.
