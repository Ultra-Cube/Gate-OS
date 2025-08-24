# Threat Model (Draft)

## Assets

- Environment manifests (integrity)
- Tokens (confidentiality)
- Telemetry data (privacy)

## Adversaries

- Local unprivileged user
- Malicious plugin author
- Supply chain attacker (dependency / image)

## Surfaces

| Surface | Current Control | Planned Control |
|---------|-----------------|-----------------|
| API Token | Random static token | Rotating / OIDC-backed |
| Plugins | Import & execute | Signature + sandbox |
| Manifests | Schema validation | Signing + policy engine |
| Containers | Dry-run / runtime call | Isolation profiles |
| Telemetry | Plain HTTP OTLP option | TLS + redact filters |

## High-Level Mitigations

- Least privilege capability allowlist
- Declarative manifests (audit friendly)
- Event telemetry for switch actions (forensics)

## Open Items

- Secure secret injection
- Encrypted at-rest state (if any persistent)
- SBOM attestation chain
