# Gate-OS Upstream Matrix

This matrix records intended integration, not a promise that every component is bundled. Exact versions, SPDX identifiers, source URLs, digests, and maintenance status must be filled before release.

| Environment | Upstream/project direction | Delivery | Gate-OS glue | License/release note |
|---|---|---|---|---|
| Everyday | Chromium/Code - OSS, LibreOffice, Thunderbird, Nextcloud, Waydroid | FOSS packages/optional images; Android apps user-provided | Manifest, launcher view, sharing policy, Waydroid lifecycle | Verify each package; GApps and proprietary apps never bundled |
| Gaming | Proton/Wine, DXVK/VKD3D, Lutris/Heroic, GameMode, MangoHud, RetroArch | FOSS optional; Steam user-downloaded | GPU/controller profile, on-demand runtime, rollback | Steam/NVIDIA proprietary components user-downloaded |
| Development | Neovim, Code - OSS/VSCodium, Podman, Forgejo/Gitea, DBeaver CE, Bruno | FOSS packages/OCI bundles | Toolchain manifest, resource limits, workspace bridge | Microsoft branded binaries require separate classification |
| Design | Blender, Krita, GIMP, Inkscape, Penpot, Scribus, Kdenlive | FOSS packages/optional services | Launcher, project shelf, GPU profile | Verify fonts, plugins, and service licenses |
| Media | Kodi, Jellyfin, VLC, OBS, Audacity | FOSS packages/optional services | Full-screen shell routing, local library, CEC/remote policy | Official integrations only; no piracy add-ons |
| Security | Wireshark, nmap, Ghidra, Metasploit, ZAP, hashcat | Isolated opt-in containers/packages | Network scope, consent, AppArmor/seccomp, audit | Offensive tools require explicit consent and legal use |
| Business | Odoo Community, Jitsi, Mattermost/Element, Nextcloud Office, Grafana/Prometheus | FOSS optional OCI/services | Dashboard, SSO, backups, resource policy | Odoo Enterprise/commercial modules never bundled |

## Review rules

1. Record exact upstream version and immutable source/digest.
2. Verify SPDX license and redistribution terms with the license auditor.
3. Generate SBOM for images and ISO package layers.
4. Review network, privilege, update, and sandbox behavior with security.
5. Mark unverified rows as target/design direction, never as shipped support.
