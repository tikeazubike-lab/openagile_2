# Phase 1 — Project Foundation

**Goal**: produce `.context/project-overview.md` and initialize the `docs/` structure.

## Questions to ask (2–3 at a time)

Round 1:
1. Project name and one-line pitch (carry forward from Phase 0 if already answered)?
2. Repo already exists, or starting from scratch?

Round 2:
3. Deployment target: self-hosted server, cloud, both, or undecided?
4. Any hard constraints already known (compliance, offline-first, specific host)?

## Output

Write `.context/project-overview.md`:

```markdown
# Project Overview: <name>

## Purpose
<one paragraph>

## Primary Users
<from Phase 0>

## Deployment Target
<answer from Q3>

## Constraints
<answer from Q4, or "None identified yet">

## Status
Phase 1 complete — <date>
```

Also create the empty `docs/` tree:
```
mkdir -p docs/decisions docs/handovers docs/testing/acceptance docs/testing/features
```

Show the user the first 20 lines of `project-overview.md` before confirming.

## Checklist before moving to Phase 2

- [ ] `.context/project-overview.md` written and confirmed
- [ ] `docs/` folder structure created
- [ ] Deployment target stated (even if "undecided")
