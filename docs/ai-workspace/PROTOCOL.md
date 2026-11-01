# AI Workspace Protocol

## Task template

- **Goal:** one measurable user or engineering outcome.
- **Owner agent:** one accountable specialist.
- **Inputs:** files, interfaces, decisions, and evidence.
- **Outputs:** exact files/artifacts and handoff summary.
- **Acceptance criteria:** commands, behavior, screenshots, or review gates.
- **Risks:** security, license, privacy, compatibility, and rollback risks.

## Handoff rules

The producing agent reports summary, changed files, commands/results, open risks, and the next owner. The receiving agent verifies the evidence instead of trusting prose. The Orchestrator integrates overlapping changes and updates `docs/ROADMAP.md`.

## Definition of done

Tests pass; meaningful coverage does not decrease; docs and changelog are updated; new dependencies and network/privilege surfaces have security and license review; manifests are signed/pinned; UI work has accessibility and screenshots; release work has SBOM, checksums, signatures, and rollback notes.

## Pull request checklist

- [ ] Correct branch and conventional commit.
- [ ] Existing tests run before and after.
- [ ] Focused tests and lint pass or failures are documented.
- [ ] Security and license reviewers approve affected surfaces.
- [ ] No secrets or unverified claims.
- [ ] Docs, roadmap, ADRs, and third-party matrix are current.
- [ ] Reversible deployment/upgrade path exists.

## Checkpoint report

1. **Checkpoint and scope**
2. **Completed work and changed files**
3. **Evidence:** exact commands and results
4. **Plan/roadmap changes**
5. **Open risks and residual uncertainty**
6. **Decision needed:** one concise question, or `None`
7. **Next phase owner and entry criteria**
