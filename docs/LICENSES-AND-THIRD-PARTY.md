# Licenses and Third-Party Components

This register is a release gate, not a claim that every item is currently bundled. Each component must have verified source, version, SPDX identifier, and redistribution terms before inclusion in an ISO or shipped image.

## Classification

- **FOSS-bundled:** redistributable in the Gate-OS image after license and notice review.
- **FOSS-optional:** available through a user-enabled download or environment bundle; still requires provenance and license review.
- **Proprietary-user-downloaded:** never redistributed by Gate-OS; the user obtains it directly under its own terms.

## Initial register

| Component/category | Intended use | Classification | Evidence/status |
|---|---|---|---|
| Gate-OS manager | Core manager | FOSS-bundled | GPL-3.0-or-later; repository `LICENSE` and `pyproject.toml`. |
| PyYAML | Manifest parsing | FOSS-bundled | Verify SPDX and notices at lock/release time. |
| jsonschema | Manifest validation | FOSS-bundled | Verify SPDX and notices at lock/release time. |
| python-jose with cryptography extra | JWT/JWKS validation | FOSS-bundled | Added during Phase 6; verify exact transitive licenses and notices before release. |
| MkDocs Material and revision plugin | Documentation build | FOSS-optional | Added as a docs extra; verify exact versions and transitive licenses in the docs build environment. |
| FastAPI/Uvicorn/Pydantic | Optional API stack | FOSS-bundled | Verify exact versions and transitive licenses before ISO inclusion. |
| Podman/Docker | Container runtime | FOSS-optional | Podman preferred; Docker distribution and daemon terms require separate review. |
| Ubuntu base packages | ISO base | FOSS-bundled subject to package licenses | Generate package-level SBOM and notices from the exact build. |
| GTK4/Libadwaita/Qt/QML | Desktop UI options | FOSS-bundled/optional by selected shell | Record selected shell and package licenses in the image manifest. |
| AppArmor/systemd | OS security/runtime | FOSS-bundled | Ubuntu package provenance and version required. |
| Waydroid/Android images | Everyday/Gaming | FOSS-optional | Image and GApps provenance must be reviewed; Google services are not bundled. |
| Chromium/Code - OSS/LibreOffice/Kodi/Blender/Krita/GIMP | Environment tools | FOSS-bundled or optional per package | Verify each exact package and trademark/asset terms. |
| Steam | Gaming client | Proprietary-user-downloaded | Never redistributed by the Gate-OS ISO. |
| NVIDIA proprietary driver | Optional hardware support | Proprietary-user-downloaded | User obtains from NVIDIA or Ubuntu source under applicable terms. |
| DaVinci Resolve/Spotify/Widevine/GApps | Optional integrations | Proprietary-user-downloaded | Never redistributed; document only lawful official installation paths. |
| Burp Suite Pro and similar commercial tools | Security environment | Proprietary-user-downloaded | No redistribution and no piracy guidance. |
| Fonts/icons/wallpapers | Branding/UI | Pending per asset | Record SPDX/source and attribution before bundling. |
| OCI images | Environment runtimes | Pending per digest | Require immutable digest, SBOM, source, and license metadata. |

## Release checklist

- [ ] Exact version/digest and source URL recorded.
- [ ] SPDX identifier and license text/notice requirements verified.
- [ ] Bundled vs optional vs proprietary classification approved.
- [ ] SBOM includes the component and transitive dependencies.
- [ ] Security review completed for network, privilege, sandbox, and update behavior.
- [ ] License auditor approval recorded in the release/checkpoint report.
