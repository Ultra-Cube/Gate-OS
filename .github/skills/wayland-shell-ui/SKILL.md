---
name: wayland-shell-ui
description: "Use when evaluating or building a Gate-OS Wayland shell, panel, dock, launcher, compositor integration, or layer-shell UI."
---

## Procedure
Compare KDE, GNOME, COSMIC, wlroots, and custom Qt/GTK options by maintenance, accessibility, theming, and hardware acceptance. Prototype top candidates; document compositor assumptions; implement persistent sidebar and escape path.

## Pitfalls
Treating Waybar as universal, assuming compositor-specific protocols, or hiding the recovery path during environment switches.

## Verification
Keyboard/touch/RTL/high-contrast tests, compositor startup logs, screenshot review, and switch failure recovery.
