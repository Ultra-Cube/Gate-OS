---
applyTo: "**/*.sh,packaging/**"
description: "Shell and packaging conventions for Gate-OS"
---

Use Bash strict mode where compatible, quote variables, check command failures, and make privilege requirements explicit. Prefer idempotent scripts with dry-run support. Run ShellCheck. Never embed credentials or download unsigned artifacts. Pin repositories and verify checksums/signatures for release inputs.
