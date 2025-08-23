# Contributing to Gate-OS (Ultra-Cube Tech)

Thank you for your interest in contributing to **Gate-OS**. We welcome code, docs, design,
security reviews, packaging, and performance tuning. This guide focuses on the Gate-OS
repository; for organization‑wide processes see other project docs.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)  
- [How You Can Help](#how-you-can-help)
- [Getting Started](#getting-started)  
- [Reporting Issues](#reporting-issues)  
- [Suggesting Enhancements](#suggesting-enhancements)  
- [Branching & Naming Conventions](#branching--naming-conventions)  
- [Submitting a Pull Request](#submitting-a-pull-request)  
- [Coding Standards](#coding-standards)  
- [Testing](#testing)  
- [Documentation](#documentation)  
- [Community & Communication](#community--communication)  
- [License](#license)  

---

## Code of Conduct

All contributors must follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues: see
[SECURITY.md](SECURITY.md). For substantial design changes create an RFC (see `rfcs/`).

---

## How You Can Help

- **Report bugs** you encounter or errors in documentation.  
- **Suggest new features** or improvements to existing functionality.  
- **Write code**: fix issues, build new features, optimize performance.  
- **Improve documentation**: clarify guides, add examples, translate content.  
- **Create tutorials** and sample scripts showing environment manifests & switching.  
- **Author RFCs** for architectural changes.
- **Security hardening**: profiles, AppArmor/SELinux suggestions.

---

## Getting Started

1. Fork `Ultra-Cube/Gate-OS`.  
2. Clone your fork:  

   ```bash
   git clone https://github.com/<your-username>/Gate-OS.git
   cd Gate-OS
   ./scripts/setup-dev-env.sh   # creates virtualenv, installs tooling (once available)
   ```

3. Create a focused branch:  

   ```bash
   git checkout -b feat/env-switch-metrics
   ```

4. Implement & add/update tests.
5. Run lint & security scan (future CI helpers).

---

## Reporting Issues

Before filing a new issue, search existing issues to avoid duplicates. When you open an issue,
please use the template and include:

- **Title**: Clear and descriptive (e.g., “Switch: latency spike when activating media env”).  
- **Description**: What happened, why it’s a problem, and any relevant background.  
- **Steps to Reproduce**: Minimal steps or code snippets to trigger the issue.  
- **Expected vs. Actual Behavior**.  
- **Environment**: OS, browser, node/python version, or other dependencies.  

---

## Suggesting Enhancements

Use our enhancement template to propose features or major changes. Include:

- **Motivation**: What problem does this solve for multi-environment workflows?  
- **Specification**: High-level description, API design, UI/UX mockups if applicable.  
- **Alternatives Considered**.  
- **Impact**: Compatibility, performance, security implications.  

---

## Branching & Naming Conventions

We follow a simple, descriptive branch naming scheme:

| Type | Prefix | Example |
|------|--------|---------|
| Feature | `feat/` | `feat/env-manifest-validation` |
| Bugfix | `fix/` | `fix/null-profile-crash` |
| Documentation | `docs/` | `docs/add-manifest-schema` |
| Refactor | `refactor/` | `refactor/extract-switcher` |
| Chore | `chore/` | `chore/update-licenses` |
| Security | `sec/` | `sec/hardening-apparmor` |

---

## Submitting a Pull Request

1. Push your branch to your fork:  

   ```bash
   git push origin feature/123-add-new-endpoint
   ```  

2. Open a pull request against the `main` branch of the upstream repository.  
3. In your PR description:
   - Reference related issues (e.g., “Closes #123”).  
   - Summarize your changes and rationale.  
   - List any breaking changes or migration steps.  
4. Fill out the PR template, including a **Checklist**:  
   - [ ] I have read the [Contributing Guidelines](#contributing-to-gate-os-ultra-cube-tech).  
   - [ ] My code follows project coding standards.  
   - [ ] I have added tests where applicable.  
   - [ ] Documentation is updated if necessary.  
5. Engage in review: respond to feedback, update your branch, and re-request review when ready.  

---

## Coding Standards

- **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/)
   (e.g., `feat: add manifest validator`).  
- **JavaScript/TypeScript**: Follow ESLint and Prettier configurations provided in the repo.  
- **Python**: Adhere to PEP8 conventions; use `flake8` and `black`.  
- **APIs**: Maintain consistent naming, error handling, and OpenAPI schema compliance where applicable.  

---

## Testing

- **Unit Tests**: Required for new Python logic (e.g., manifest utilities).  
- **Running Tests**: `pytest -q` after `pip install .[dev]`.  
- **Manifest Validation**: `gateos validate examples/environments/*.yaml --schema
   docs/architecture/schemas/environment-manifest.schema.yaml`  
- **CI**: Pipeline enforces Ruff, markdownlint, yamllint, schema validation, SBOM generation,
   and vulnerability scan (fails on High severity).  

---

## Documentation

- All user-facing documentation lives in `docs/`. Architecture schema:
   `docs/architecture/schemas/environment-manifest.schema.yaml`.  
- Update relevant guides, add code samples, and verify links.  
- For SDKs, include usage examples and API reference in Markdown.  

---

## Community & Communication

Stay connected and get help:

- Slack: [join.ultra-cube](https://join.slack.com/t/ultra-cube/shared_invite/)  
- GitHub Discussions: <https://github.com/Ultra-Cube/info/discussions>  
- Email: <support@ucubetech.com>  

We also host regular contributor calls—watch for announcements on Slack and our Twitter feed.

---

## License

By contributing you agree your work is released under **GPLv3** (core) unless explicitly stated
otherwise in a separate extension license. See [LICENSE](LICENSE).

---

Thank you for helping build Gate-OS. Your contributions make multi-environment workflows first-class on Linux. 🐧🚀
