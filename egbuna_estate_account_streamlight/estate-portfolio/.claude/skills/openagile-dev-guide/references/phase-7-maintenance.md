# Phase 7 — Maintenance

**Goal**: keep `.context/` and `docs/` accurate as the project evolves after initial delivery,
and route new work back through Phase 4 rather than letting maintenance become vibecoding by
another name.

## Triggers for entering Phase 7 workflows

- A bug report against an already-accepted feature
- A request to modify existing behavior (not a brand-new feature)
- Dependency/security updates
- A new AI agent joining an already-mature project (route to Phase 3's "onboard agent" mode,
  but skip the phases already complete — extract context from `.context/` instead of re-asking)

## Bug fix protocol

1. Identify which F-XXX the bug belongs to. If it doesn't map to an existing feature, that's a
   signal the original spec had a gap — note it.
2. Write a new scenario in the existing `.feature` file (via gherkin-spec-agent) that currently
   fails, reproducing the bug as a failing test — **not** a manual repro script.
3. Fix the code until that scenario passes, following the same red→green discipline as Phase 5.
4. Amend the AT file as `AT-XXX-N` (never edit the original AT in place).

## Dependency / infra maintenance

For routine dependency bumps, security patches, or infra config changes that don't change
observable behavior: no new spec is required, but log the change in
`.context/progress-tracker.md` under a "Maintenance Log" section (add it if it doesn't exist)
so there's a record separate from the feature table.

## When maintenance reveals architecture drift

If repeated fixes are hitting the same friction point, that's a signal to write a new ADR
(`docs/decisions/ADR-XXX.md`) documenting the drift and the decision to address or accept it —
don't let architecture silently rot without a record of why.

## Checklist for each maintenance cycle

- [ ] Bug reproduced as a failing test before any fix is written
- [ ] Fix verified against that test, not just manually
- [ ] AT amended (if behavior-visible) or maintenance log updated (if not)
- [ ] Architecture drift, if any, captured in a new ADR
