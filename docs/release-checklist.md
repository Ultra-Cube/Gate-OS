# Release Checklist

Use this checklist for every Gate-OS release. Each item must be checked off before tagging.

---

## Pre-Release

### 1. Code Quality
- [ ] All tests pass: `make test` (expect 0 failures, >= 95% coverage)
- [ ] Lint clean: `make lint` (expect 0 errors)
- [ ] No `TODO(release)` comments in codebase: `grep -r "TODO(release)" gateos_manager/`
- [ ] Dependency audit clean: `pip-audit` (0 known vulnerabilities)
- [ ] Security scan clean: Grype GitHub Actions job passes

### 2. Documentation
- [ ] `CHANGELOG.md` updated with all changes under `[Unreleased]`
- [ ] New `## [X.Y.Z] - YYYY-MM-DD` section added in `CHANGELOG.md`
- [ ] `docs/` updated for any new/changed features
- [ ] `mkdocs build --strict` produces no warnings
- [ ] Version in `pyproject.toml` updated

### 3. Manifest & Schema
- [ ] Example manifests validate: `gateos validate environments/*.yaml`
- [ ] JSON Schema version in `environment-manifest-v1.0.yaml` matches if schema changed

---

## Release

### 4. Version Bump
```bash
# Edit pyproject.toml: version = "X.Y.Z"
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): bump version to vX.Y.Z"
```

### 5. Tag
```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin main --tags
```

### 6. GitHub Release
- [ ] Draft GitHub Release from tag `vX.Y.Z`
- [ ] Copy CHANGELOG.md section for this version into release notes
- [ ] Attach SBOM artifact (`sbom.json`) from CI
- [ ] Attach Grype vulnerability report (`vuln-report.json`) from CI
- [ ] Publish release

### 7. Docs Deploy
```bash
mkdocs gh-deploy --force
```
- [ ] Verify [https://ultra-cube.github.io/Gate-OS/](https://ultra-cube.github.io/Gate-OS/) is updated

---

## Post-Release

### 8. Verify
- [ ] `gateos check-update` reports new version from GitHub Releases API
- [ ] GitHub Actions CI badge on README is green
- [ ] PyPI package (when published): `pip install gate-os==X.Y.Z` works

### 9. Announce
- [ ] GitHub Discussions / Announcements post
- [ ] Update Discord / community channels
- [ ] Update project roadmap (mark milestone complete)

---

## Hotfix Process

For critical bugfixes:

```bash
git checkout -b hotfix/vX.Y.Z+1 vX.Y.Z
# fix commit
git tag -a vX.Y.Z+1 -m "Hotfix vX.Y.Z+1"
git push origin hotfix/vX.Y.Z+1 --tags
# Open PR to merge hotfix back to main
```

---

## Version Numbering

Gate-OS follows **Semantic Versioning** (semver):

| Version bump | When |
|---|---|
| `MAJOR` (X.0.0) | Breaking API or manifest schema changes |
| `MINOR` (x.Y.0) | New features, backward-compatible |
| `PATCH` (x.y.Z) | Bug fixes, security patches, documentation |

Pre-releases: `X.Y.Z-beta.1`, `X.Y.Z-rc.1`

---

## See Also
- [Contributing](contributing.md) — development workflow
- [Changelog](changelog.md) — version history
- [Supply Chain](architecture/supply-chain.md) — release artifact signing
