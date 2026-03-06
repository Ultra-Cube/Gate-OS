# Contributing to Gate-OS

Thank you for your interest in contributing to Gate-OS!

---

## Quick Start

```bash
git clone https://github.com/Ultra-Cube/Gate-OS.git
cd Gate-OS
make setup          # creates .venv + installs dev deps
source .venv/bin/activate
make test           # run all 308 tests
make lint           # ruff + flake8
```

---

## Development Requirements

- Python 3.11+
- Linux (Ubuntu 22.04+ or Fedora 38+)
- `make` (GNU Make)
- `git`

All development dependencies are in `requirements-dev.txt` and installed by `make setup`.

---

## Repository Structure

```
Gate-OS/
├── gateos_manager/          # Core package
│   ├── api/                 # FastAPI control API + WebSocket
│   ├── containers/          # Container runtime abstraction
│   ├── manifest/            # Manifest loader + schema validator
│   ├── plugins/             # Plugin registry + entry-point discovery
│   ├── profiles/            # Hardware profile (CPU, GPU, NIC)
│   ├── security/            # Signing, isolation, policy
│   ├── services/            # systemd service manager
│   ├── telemetry/           # OTLP, Prometheus
│   └── updater.py           # OTA update logic
├── environments/            # Example environment manifests
├── tests/                   # pytest test suite (308 tests)
├── docs/                    # MkDocs documentation source
├── scripts/                 # Dev helper scripts
├── Makefile
└── pyproject.toml
```

---

## Testing

Gate-OS requires **95% test coverage** on all PRs.

```bash
make test                    # run all tests with coverage
make test-fast               # run tests without coverage (faster)
pytest tests/test_orchestrator.py -v   # run a specific test file
```

Coverage report is written to `htmlcov/index.html`.

### Test Conventions
- Tests live in `tests/`; filename mirrors module: `test_<module>.py`
- Use `pytest` fixtures; mock external calls (`systemctl`, `podman`, HTTP) with `unittest.mock`
- Dry-run mode via `monkeypatch.setenv("GATEOS_DRY_RUN", "1")` for integration tests

---

## Linting

```bash
make lint    # ruff + flake8
make fmt     # ruff --fix (auto-format)
```

Pre-commit hooks run lint + format automatically on `git commit`.

---

## Pull Request Process

1. **Fork** the repository and create a feature branch:
   ```bash
   git checkout -b feat/my-feature
   ```

2. **Write tests first** (TDD encouraged) — cover the happy path AND error cases.

3. **Ensure all checks pass**:
   ```bash
   make test && make lint
   ```
   Coverage must be >= 95%.

4. **Update documentation** if you add/change behaviour:
   - Add or update docs in `docs/`
   - Update `CHANGELOG.md` (Unreleased section)
   - Update `TODO.md` if resolving a planned item

5. **Open a Pull Request** with:
   - Clear title following Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`
   - Description of what changed and why
   - Reference to any related issue: `Closes #123`

---

## Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): short description
fix(scope): short description
docs(scope): short description
test(scope): short description
refactor(scope): short description
chore(scope): short description
```

Examples:
```
feat(security): add Ed25519 manifest signing CLI
fix(containers): handle podman not found gracefully
docs(api): add WebSocket endpoint reference
test(updater): add apply_update schedule strategy tests
```

---

## Code Style

- **Python 3.11+** — use type hints on all public functions
- **ruff** for formatting + linting (config in `pyproject.toml`)
- **Docstrings**: Google style for public APIs; omit for private functions
- **No bare `except`** — always catch specific exceptions

---

## Adding a New Feature

1. Start with the module in `gateos_manager/`
2. Add tests in `tests/test_<module>.py`
3. Add CLI command in `gateos_manager/cli.py` if user-facing
4. Add REST endpoint in `gateos_manager/api/control_api.py` if API-facing
5. Add documentation in `docs/`
6. Update `CHANGELOG.md`

---

## Reporting Bugs

Open a GitHub Issue with:
- Gate-OS version (`gateos --version`)
- OS and Python version
- Steps to reproduce
- Expected vs actual behaviour
- Relevant logs (with `GATEOS_LOG_LEVEL=DEBUG`)

---

## Security Issues

Report security vulnerabilities via GitHub Security Advisories — **not** public issues.  
See [Security Overview](security/overview.md) for details.

---

## License

Gate-OS is licensed under the **Apache 2.0 License**. By contributing, you agree your contributions will be licensed under Apache 2.0.
