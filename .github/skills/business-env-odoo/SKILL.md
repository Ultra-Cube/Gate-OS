---
name: business-env-odoo
description: "Use when integrating Odoo Community and business services into the Gate-OS Business environment."
---

## Procedure
Use Odoo Community with license boundaries documented; deploy rootless and pinned; define backups, SSO, reverse proxy, secrets, modules, and dashboard embedding; keep enterprise/proprietary modules user-provided.

## Verification
Manifest, backup/restore, auth/session, resource, upgrade, and license tests pass; no default credentials or exposed admin surface remains.
