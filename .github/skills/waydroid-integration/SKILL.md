---
name: waydroid-integration
description: "Use when integrating Waydroid for Everyday or Gaming, including images, GApps boundaries, Wayland, input, sharing, and AppArmor."
---

## Procedure
Verify Wayland and kernel prerequisites; document image provenance and licensing; install/init only on opt-in; isolate Android data; define window/full-screen and file-sharing policy; test gamepad and rollback.

## Pitfalls
Redistributing Google components, assuming X11 support, broad host mounts, and treating Android apps as trusted.

## Verification
Fresh VM or supported hardware evidence, service lifecycle tests, AppArmor logs, input/sharing tests, and uninstall cleanup.
