# Security Policy

Gate-OS takes security seriously. This document defines how to report vulnerabilities and how we process them.

## Supported Components (Initial)

- Core environment manager (planned)
- Manifest parser
- Switching service

(Pre-release: no public packages yet.)

## Reporting a Vulnerability

Email: **[security@ucubetech.com](mailto:security@ucubetech.com)**  
Use PGP (key publishing TBD) for sensitive reports.

Provide:

- Affected component/version (commit hash)
- Reproduction steps
- Impact assessment (confidentiality/integrity/availability)
- Suggested remediation (optional)

## Coordinated Disclosure Timeline (Target)

| Day | Action |
|-----|--------|
| 0 | Acknowledge receipt |
| 3 | Triage & severity assignment |
| 7 | Patch plan communicated |
| ≤30 | Fix merged & release (if code present) |
| ≤45 | Public advisory (unless embargo extended) |

## Severity (Draft Mapping)

| CVSS Range | Label |
|------------|-------|
| 9.0–10.0 | Critical |
| 7.0–8.9 | High |
| 4.0–6.9 | Medium |
| 0.1–3.9 | Low |

## Handling Non-Code Issues

- Trademark misuse → [legal@ucubetech.com](mailto:legal@ucubetech.com)
- Abuse of community spaces → [conduct@ucubetech.com](mailto:conduct@ucubetech.com)

## Security Hardening Roadmap (Excerpt)

- Signed environment manifests
- Reproducible build pipeline
- Sandboxed container profiles (seccomp/AppArmor)
- Supply-chain scanning (SBOM + vulnerability diff)

---
**Date:** July 2025 | **By:** Fadhel.SH  
**Company:** [Ultra-Cube Tech](https://ucubetech.com) | [GitHub](https://github.com/Ultra-Cube/) | [LinkedIn](https://www.linkedin.com/company/ultra-cube)
