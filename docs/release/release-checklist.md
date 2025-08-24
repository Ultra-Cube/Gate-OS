# Release Checklist (Pre-Tag)

Use this checklist before running `scripts/release.sh`.

## 1. Working Tree & Version
- [ ] `git status` clean
- [ ] `pyproject.toml` version bumped (semantic increment)
- [ ] `CHANGELOG.md` Unreleased section moved / summarized into new version section

## 2. Quality Gates
- [ ] `scripts/dev-check.sh` passes locally
- [ ] All tests green with coverage > target (adjust target as project matures)
- [ ] No TODO/FIXME in touched code (or documented in issue)

## 3. Security & Supply Chain
- [ ] CI SBOM step succeeded (see latest run artifacts)
- [ ] Grype scan shows no Critical (High reviewed / accepted if present)
- [ ] Dependency diffs reviewed since last tag

## 4. Documentation
- [ ] README updated (features, status, new env vars)
- [ ] Manifest authoring guide reflects schema changes
- [ ] Plugin dev guide updated if hooks/schema changed
- [ ] Threat model updated if new surfaces introduced

## 5. Telemetry & Observability
- [ ] New telemetry event types documented (if any)
- [ ] Batch flush logic still exercised in tests (or manual run)

## 6. Tag & Publish
- [ ] Run: `./scripts/release.sh`
- [ ] Verify tag exists on remote
- [ ] (Optional) Draft GitHub Release notes from CHANGELOG

## 7. Post-Tag
- [ ] Open new Unreleased section in `CHANGELOG.md`
- [ ] Create follow-up issues (debt, follow-on tasks)

---
Automate as project matures (GitHub Action preflight before tagging).
