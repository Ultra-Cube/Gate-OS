# Supply Chain & Integrity (Draft)

## Goals
- Reproducible environment switching
- Verifiable provenance for manifests & container images

## Planned Components
| Component | Purpose | Phase |
|----------|---------|-------|
| SBOM Generation (Syft) | Inventory dependencies | Done (CI step) |
| Vulnerability Scan (Grype) | Detect known CVEs | Done (CI step) |
| Manifest Signing | Ensure integrity & authorship | Future |
| Image Policy (Digest Pinning) | Eliminate tag drift risk | Future |
| Provenance Attestation (SLSA-ish) | Trace build pipeline | Future |

## Near-Term Actions
- Enforce digest pin requirement (warning mode) in manifests
- Add signature verification CLI stub
- Emit supply chain telemetry events (sbom_generated, scan_passed)

## Long-Term
- Chain-of-trust across environment bundles
- Transparency log for published signatures
