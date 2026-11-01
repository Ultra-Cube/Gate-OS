---
name: systemd-service-authoring
description: "Use when adding or hardening Gate-OS systemd units, sockets, timers, or service lifecycle behavior."
---

## Procedure
Define user/system ownership, dependencies, readiness, timeouts, restart policy, state paths, and rollback. Apply hardening only as compatible with the service. Validate and test under a minimal environment.

## Commands
`systemd-analyze verify`, `systemd-analyze security`, `systemctl --user`, and `journalctl` with a disposable VM or test unit.

## Verification
Unit syntax, startup/shutdown, failure recovery, permissions, logs, and uninstall cleanup are all tested.
