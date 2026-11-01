---
applyTo: "**/*.service,**/*.socket,**/*.timer,**/*.apparmor,**/apparmor/**,**/seccomp/**"
description: "Hardening rules for systemd and AppArmor/seccomp files"
---

Apply least privilege and verify units with `systemd-analyze verify` and, where possible, `systemd-analyze security`. Use NoNewPrivileges, ProtectSystem, PrivateTmp, capability bounding, device and namespace restrictions intentionally. AppArmor profiles should start in complain mode during development, then be tested and promoted to enforce. Record exceptions and rollback paths.
