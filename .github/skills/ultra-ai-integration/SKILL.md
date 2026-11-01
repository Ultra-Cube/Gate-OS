---
name: ultra-ai-integration
description: "Use when specifying or implementing Gate-OS integration with Ultra AI: UI specs, connectors, generated apps, policy gates, and routing."
---

## Procedure
Version schemas first; render only pre-approved native components; require signed connector manifests and scoped tokens; sandbox generated web apps with CSP and network allow-lists; require confirmation for high-risk actions; keep local-first and opt-in.

## Verification
Offline mock works, inputs are treated as data, actions are audited, preview/accept/revert works, and security tests cover prompt injection and capability escalation.
