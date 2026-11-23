---
type: HO
id: HO-140
title: Claude Web → OpenCode: F-026b closeout — six loose ends
date: 2026-08-28
from: Claude Web
to: OpenCode
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

## Context

F-026b (email reminder infrastructure) is functionally complete and
verified end-to-end as of HO-139 — SMTP over Mailgun confirmed via `swaks`
and the real `/api/v1/admin/reminders/test-send` endpoint, cron confirmed
installed and dry-run clean, RED-GREEN-compliant tests in place for AC-2/3/4.
It is **not yet formally closed**. HO-136 raised six loose ends that were
never resolved because the thread was overtaken first by the Mailgun
credential incident, then by the `.env.v3` secret-exposure incident, then
by the login-failure diagnosis. This handover consolidates all six into one
request. **F-026b does not close until every item below has a raw-evidence
answer**, per standing governance rules (raw command output only — no
narrated summaries).

Respond via the next handover in the Handover Chain, referencing HO-140.

---

## Item 0 (highest priority) — Confirm `.env.v3` is untracked

This has been recommended **twice** (HO-135's own suggestion, then required
explicitly as HO-136 Item 0 step 4) and confirmed executed in **zero**
handovers since. Until this is confirmed, the repo is one careless commit
away from re-exposing `JWT_SECRET`, the `DATABASE_URL` password, and
`EPM_ADMIN_PASSWORD` again — the exact incident class already lived through
this session.

Required evidence:
```
git ls-files | grep -F '.env.v3'   # must return nothing
cat .gitignore | grep -F '.env.v3' # must show it present
git log --all --oneline -- .env.v3 | head -20   # confirm no tracked history remains post-filter-branch, or explain what does
```
If `.env.v3` is still tracked, run `git rm --cached .env.v3` and add the
`.gitignore` entry now, then re-run the checks above and report all three
raw outputs. Do not report this item closed on narration alone.

---

## Item 1 — Full 40-character SHAs for the six post-`filter-branch` commits

Short-form hashes given so far: `ef6adc3`, `76b80db`, `c6e3800`, `d061d7e`,
`34c5352`, `7fc846d`.

**This is the fourth time this has had to be requested across this
feature's handover chain** (`345c194`, `c67dd93`, and now every hash in
HO-135/HO-139 needing re-resolution). This is being named explicitly as a
standing compliance pattern with this builder session, not a one-off typo
— if it recurs a fifth time, it needs to be escalated as a process issue
rather than corrected again in the next handover.

Required evidence:
```
git log --format='%H %s' -6
```
Report the full output, matched against the six short hashes above so each
one is unambiguously resolved to its 40-character form.

---

## Item 2 — F-TD-001 commit reconciliation

HO-135 mentioned "F-TD-001" among commits sitting on `test` but not yet in
`main`. F-TD-001 was declared fully closed in MASTER_CONTEXT v4.10
(HO-125, commit `8dcbdf7abf3290906e0d6d18f23754e143e3df1f`). Confirm whether
this is the *same* teardown work, or something else entirely.

Required evidence:
```
git log main..test --oneline | grep -i 'td-001\|testbuild'
git branch --contains 8dcbdf7abf3290906e0d6d18f23754e143e3df1f
```
If the commit(s) on `test` are the same teardown work: the functional work
already happened (direct VPS execution, per the standing workstation-offline
exception) — what's missing is only the git record. Open a small
reconciliation PR that merges just this into `main` so the "closed"
declaration and the actual merged state agree. Do not bundle this into the
F-026b PR — separate PR, separate commit, one-feature-per-session still
applies.

---

## Item 3 — F-026b PR shape

HO-136 recommended cutting a clean `feature/f-026b` branch, cherry-picked
from `main`, rather than opening `test → main` directly (which would pull
in ~13 unrelated commits).

Required evidence — one of:
```
git log --oneline feature/f-026b -20   # if this branch exists
```
or, if a different shape was used, state exactly what happened and show
the actual PR diff scope:
```
gh pr view <PR#> --json baseRefName,headRefName,commits
```
Confirm the PR does **not** carry in unrelated `test` commits beyond
F-026b's own work (and, if Item 2 applies, beyond the reconciled F-TD-001
commit if it's deliberately included).

---

## Item 4 — Bug-fix PR #8 status

`bugfix/production-bugs-001` (covering `BUG-TZ-NAIVE-001`,
`BUG-HOLDING-STATUS-001`, `BUG-PDF-UPLOAD-500-001`) was opened per HO-135.
Status since then is unconfirmed — reviewed, merged, still open?

Required evidence:
```
gh pr view bugfix/production-bugs-001 --json state,mergedAt,reviews
```
or equivalent raw `git log main --oneline` showing the merge commit if
already merged. If still open, state what's blocking it.

---

## Item 5 — 215 → 207 test-count reconciliation

Removing the bug-fix hunks from the F-026b branch dropped the reported
count by 8, but only 6 regression tests were described as bug-proving. The
arithmetic was never actually reconciled (HO-136 item 4 raised this,
unanswered since).

Required evidence:
```
pytest --collect-only -q | tail -5   # on the branch as it stands post-split
git diff main feature/f-026b -- tests/ | grep -c '^+def test_\|^-def test_'
```
Explain the discrepancy explicitly — which 2 tests account for the gap
between 8 removed and 6 attributed, and why.

---

## Closing criteria

F-026b is not marked closed in MASTER_CONTEXT until:
- Item 0 shows raw confirmation `.env.v3` is untracked and gitignored
- Item 1 provides all six full SHAs
- Item 2 is either resolved as "not applicable" (different work) or has a
  reconciliation PR merged with its own commit hash
- Item 3 confirms actual PR scope
- Item 4 confirms bug-fix PR #8's real state
- Item 5's arithmetic is explained, not just re-stated

Report back via the next number in the Pre-assigned HO numbers buffer
(HO-141, from the HO-126–155 general-purpose block) — do not self-assign.
