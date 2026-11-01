---
name: license-audit
description: "Use when reviewing dependencies, fonts, icons, images, container layers, upstream projects, or ISO redistribution rights."
---

## Procedure
Collect source URL, version, SPDX identifier, license text, copyright, redistribution conditions, and whether it is bundled or user-downloaded. Update `docs/LICENSES-AND-THIRD-PARTY.md` and required notices.

## Verification
`reuse lint` or equivalent passes where configured, matrix entries have evidence, and the license auditor approves new distributable content.
