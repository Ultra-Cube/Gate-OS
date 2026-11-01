---
name: qt-qml-or-gtk-ui
description: "Use when implementing Gate-OS sidebar, launcher, settings, or shell UI in Qt6/QML or GTK4/Libadwaita."
---

## Procedure
Choose technology through an ADR; map design tokens; build accessible components; expose native approved actions only; support themes, RTL, keyboard, touch, and reduced motion; screenshot test key states.

## Verification
Build on documented Ubuntu packages, run UI tests or a reproducible manual matrix, inspect focus order and scalable text, and test failure/rollback feedback.
