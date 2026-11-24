# Phase 6 — Acceptance / Deployment

**Goal**: produce acceptance tests (`AT-XXX.md`) distinct from the unit/integration tests
generated in Phase 4, and get the feature deployed.

## Why AT files are separate from the generated test suite

The Phase 4/5 tests (from gherkin-spec-agent) prove the code does what the spec says at the
unit/integration level. Acceptance tests are the human-readable checklist a person (you, or a
stakeholder) walks through against the running system — they catch integration and UX issues
the automated suite doesn't cover (does it *feel* right, not just pass assertions).

## Questions to ask (2–3 at a time)

Round 1:
1. Who signs off on this feature before it's considered done — just you, or someone else?
2. Deploy target for this feature: same as project default, or does it need something special
   (migration, feature flag, env var)?

## Output

Write `docs/testing/acceptance/AT-XXX.md` (matching the feature's F-XXX number, e.g. `AT-005`
for `F-005`). Use immutable numbering — `AT-005-1`, `AT-005-2` for any amendment, never edit
the original in place:

```markdown
# AT-XXX: <Feature Name> Acceptance

## Preconditions
<what must be true before testing, e.g. "seed data loaded, user logged in as admin">

## Checklist
- [ ] <observable behavior 1, phrased as a user action + expected result>
- [ ] <observable behavior 2>
- [ ] Deployed to <target> and verified in that environment (not just local)

## Sign-off
- Tested by: ____
- Date: ____
- Result: Pass / Fail / Pass with notes
```

Then walk the deployment:

```bash
# example — adapt to the project's actual deploy mechanism from .context/architecture.md
docker compose build
docker compose up -d
docker compose logs -f --tail=50
```

Confirm the deployed feature against the AT checklist before marking it accepted.

## Checklist before moving to Phase 7 (or looping back to Phase 4 for the next feature)

- [ ] `AT-XXX.md` written and checklist walked
- [ ] Feature deployed to its target environment
- [ ] `.context/progress-tracker.md` — Accepted = ✅ for this feature
- [ ] If this was the last feature in the current backlog, proceed to Phase 7; otherwise loop
      back to Phase 4 for the next feature
