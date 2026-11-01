# Checkpoint 4 — Concept UI Design

**Status:** Pending rendered screenshot evidence and maintainer approval  
**Date:** 2026-11-01  
**Branch:** `docs/phase4-concept-ui`

## Completed

- Added source design tokens in `docs/design/tokens.json` and CSS variables in `tokens.css`.
- Added a responsive HTML concept for the main desktop and persistent seven-environment sidebar.
- Included light/dark/high-contrast token directions, RTL-safe logical properties, keyboard focus, touch-sized controls, and reduced-motion behavior.
- Added a design README that labels all visuals as concepts and lists remaining design states.
- Linked the concept gallery from MkDocs navigation.
- Added `.github/workflows/docs-and-design.yml` to build MkDocs strictly and render light/dark/contrast/mobile RTL screenshots with Playwright in CI.

## Evidence

- JSON token parsing and HTML structure checks are pending the local validation command.
- Existing project tests are unaffected and remain 394 passing from the previous checkpoint.
- Playwright screenshot rendering is delegated to the CI workflow; local WSL rendering remains unavailable.

## Remaining work

- Render desktop/mobile, RTL, dark, and high-contrast screenshots with Playwright MCP or CI.
- Add per-environment launcher concepts, AI surfaces, installer, first-run, and rollback states.
- Evaluate two shell technologies and record an ADR before implementation.

## Decision needed

Approve the visual direction and authorize Phase 5 optional AI-native prototype work after screenshot/accessibility evidence is available.