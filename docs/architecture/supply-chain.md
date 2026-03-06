# Supply Chain & Integrity

> **Status:** Active — last reviewed March 2026 (v1.2.0)

---

## Goals

- Reproducible environment switching via declarative, schema-validated manifests
- Cryptographically verifiable provenance for manifests, container images, and the Gate-OS package itself
- Automated vulnerability detection in CI before every release

---

## Implemented Controls (v1.2.0)

| Component | Purpose | Status |
|---|---|---|
| **Ed25519 Manifest Signing** | Ensure integrity & authorship of YAML manifests | ✅ Done (`gateos sign/verify/gen-keypair`) |
| **Schema Validation** | Prevent malformed manifests from reaching the switch engine | ✅ Done (jsonschema + `gateos validate`) |
| **SBOM Generation (Syft)** | Inventory all Python/OS dependencies | ✅ CI step (`.github/workflows/`) |
| **Vulnerability Scan (Grype)** | Detect known CVEs in dependencies | ✅ CI step |
| **pip-audit** | Check PyPI packages against OSV advisory database | ✅ Dev check (`scripts/dev-check.sh`) |
| **Pinned dependencies** | `requirements.txt` with hashes | ✅ Done |
| **Telemetry supply chain events** | `sbom_generated`, `scan_passed` events emitted | ⏳ v1.3.0 |

---

## Manifest Signing Workflow

```bash
# Generate a keypair (once per deployment)
gateos gen-keypair --key-dir /etc/gateos/keys/

# Sign a manifest before distributing
gateos sign environments/gaming.yaml --key-dir /etc/gateos/keys/
# → writes environments/gaming.yaml.sig

# Verify before switch (automated by switch engine in v1.3.0)
gateos verify environments/gaming.yaml --key-dir /etc/gateos/keys/
# → OK: signature valid for environments/gaming.yaml
```

Keys are **Ed25519** (NaCl / PyNaCl). The private key (`signing.key`) stays on the signing machine; the public key (`signing.pub`) is distributed with the deployment.

---

## Container Image Integrity

### Current State
- Images are referenced by name + tag in manifests (e.g., `redis:7`).
- No digest enforcement yet.

### Planned (v1.3.0)
- Warn when manifest image lacks `@sha256:` digest pin.
- Add `imagePolicy: require-digest` manifest field.
- Emit `container.image.digest_missing` telemetry event when tag-only refs are used.

---

## CI/CD Integrity Pipeline

```
Push / PR
  │
  ├── pytest (308 tests, 95% coverage)
  ├── pip-audit (OSV advisory check)
  ├── Syft SBOM generation → sbom.json artifact
  ├── Grype vulnerability scan → vuln-report.json artifact
  └── Release:
        ├── Build wheel (hatchling)
        ├── Sign with Ed25519 (manifest + wheel hash)
        ├── Attach SBOM + sig to GitHub Release assets
        └── Publish to PyPI (planned)
```

---

## Planned Controls (v1.3.0+)

| Component | Purpose | Phase |
|---|---|---|
| Digest pin enforcement | Eliminate container image tag drift | v1.3.0 |
| Plugin signature verification | Block unsigned plugins before load | v1.3.0 |
| SLSA provenance attestation | Trace build pipeline to release | v1.4.0 |
| Transparency log | Published signatures + attestations | v1.4.0 |
| TLS OTLP transport | Encrypt telemetry in transit | v1.3.0 |

---

**Date:** March 2026 | **By:** Fadhel.SH
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/)

