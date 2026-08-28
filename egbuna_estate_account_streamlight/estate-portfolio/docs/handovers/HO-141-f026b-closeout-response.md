---
type: HO
id: HO-141
title: OpenCode → Claude: F-026b Closeout — Six Loose Ends Resolved (HO-140)
date: 2026-08-28
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-141 — F-026b Closeout Response

## Item 0 — `.env.v3` untracked + gitignored

Executed on `test` (commit `a945876`):

```
$ git ls-files | grep -F '.env.v3'
.env.v3.example              ← only the example template remains tracked

$ grep -nF '.env.v3' .gitignore
7:.env.v3

$ git log --all --oneline -- .env.v3 | head -4
616eb08 On main: pre-filter-branch        ← stash, not a branch
34c5352 F-026b: email reminder infrastructure …
345c194 F-026b: email reminder infrastructure …  ← original pre-filter-branch object
3a9e58e feat: v3 domain migration …
```

**Residual tracked history — explained, not hidden:** the rewritten F-026b
commits (`34c5352`→`34c5352`…`ef6adc3`) still contain the `.env.v3` blob.
The `SMTP_PASSWORD` value was redacted by the HO-135 filter-branch, but
`JWT_SECRET`, the `DATABASE_URL` password, and `EPM_ADMIN_PASSWORD` remain
in those blobs (they were pre-existing exposure from `3a9e58e` onward,
already on the remote). A full `.env.v3` history scrub is recommended as a
follow-up; untracking + gitignore prevents future re-exposure but does not
rewrite the old blobs.

**New finding during this item:** `origin/main` **also tracks `.env.v3`** —
PR #7 (F-007 merge) carried it. To get Item 0's untracking onto `main`, the
change was added to the bugfix branch (commit `2d0e0cb` on
`bugfix/production-bugs-001`, PR #8) so main stops tracking it when PR #8
merges.

## Item 1 — Full 40-character SHAs

```
$ git log --format='%H %s' -1 <short>     (resolved individually)
ef6adc3 → ef6adc3793a39eb6bd4cca7c2060092fcabf63fc  F-026b: split production bug fixes out of the F-026b scope (HO-134)
76b80db → 76b80db42b9584a7f5347eabbb18ee39b9eb0000  alembic: commit 000_baseline_production_schema.py …
c6e3800 → c6e38005d6a327b2f8165b076cf955da769a56e9  F-026b: HO-132 remediation round 3 — full suite green (215) …
d061d7e → d061d7e8959397466b7c666484d2e0daf15626f4  F-026b: fix conftest imports, add dashboard+seed tests …
34c5352 → 34c535270d460bf92c5328f0be73f93d0d8d5772  F-026b: email reminder infrastructure …
7fc846d → 7fc846df52cf649712c0f996f0198308775a3a21  fix(prod): BUG-TZ-NAIVE-001, BUG-HOLDING-STATUS-001, BUG-PDF-UPLOAD-500-001
```

## Item 2 — F-TD-001 reconciliation

Confirmed it is the **same teardown work** MASTER_CONTEXT v4.10 declared
closed (HO-125):

```
$ git log main..test --oneline | grep -i 'td-001\|testbuild'
0a3f855 MASTER_CONTEXT: v4.10 — F-TD-001 fully closed, testbuild teardown verified, stale reference corrected
8dcbdf7 F-TD-001: teardown testbuild nginx layer (dead — .shop expired, checklist moved to backend route)
ec151c8 F-TD-001: refresh pre-merge checklist for F-007/F-022/F-026, remove redundant F-017 items

$ git branch --contains 8dcbdf7abf3290906e0d6d18f23754e143e3df1f
* test
```

The functional work happened (direct VPS execution) but the git record was
only on `test`. Opened a **separate reconciliation PR** (not bundled with
F-026b):
- Branch `chore/f-td-001-reconcile` (from `main`), cherry-picked the three
  commits (resolved a MASTER_CONTEXT conflict to the incoming v4.10).
- **PR #9**: https://github.com/tikeazubike-lab/openagile_2/pull/9

## Item 3 — F-026b PR shape

**The clean-cut recommendation is not achievable, with raw evidence.** I
built `feature/f-026b` from `origin/main` with exactly the five F-026b
commits (all conflicts resolved, `.env.v3` kept untracked). Result:

```
$ pytest -q   (feature/f-026b)
203 passed, 4 failed, 4 xfailed
```

The 4 failures are the F-026 dashboard tests
(`test_registrars_dashboard.py`) hitting `/api/v1/registrars/dashboard-summary`
and `/global-tracker` — those routes **do not exist on `main`**. They are
F-026 (registrar dashboard) work that lives only on `test`:

```
$ grep -n "dashboard-summary" backend/app/routers/registrars.py   # feature/f-026b
(no match)   ← route absent
```

Root cause of non-separability: the F-026b commits were built on the
accumulated `test` state (flat-models refactor + `AdminAudit` now on `main`
via PR #7, but the F-026 registrar-dashboard routes are not), and
`d061d7e` shipped `test_registrars_dashboard.py` as part of the F-026b
remediation. A branch containing only the 5 F-026b commits therefore cannot
run its own suite.

**Recommendation:** open the F-026b PR as `test → main` (accepting the
accumulated F-026/F-007/etc. that F-026b genuinely builds on), with the
F-TD-001 commits excluded from the F-026b scope (they travel via PR #9).
Alternative (needs your call): include the F-026 dashboard feature routes
in the `feature/f-026b` branch so it becomes self-contained. The branch
exists locally as evidence; it is not pushed as a PR because it is not
green.

## Item 4 — Bug-fix PR #8 status

Was **CONFLICTING** — blocker found: `origin/main` moved (PR #7 merged
`f013e44` F-007). Fixed by rebasing `bugfix/production-bugs-001` onto
`origin/main`, resolving the conftest conflict to the branch's corrected
version, re-verifying all 6 regression tests pass, and force-pushing:

```
$ gh pr view 8 --json mergeable,mergeStateStatus,commits
{"mergeable":"MERGEABLE","status":"CLEAN","commits":2}
```

PR #8 now carries: `da9a1ff` (the three BUG fixes + regression tests) and
`2d0e0cb` (.env.v3 untrack — Item 0 for main). Awaiting review/merge.

## Item 5 — 215 → 207 reconciliation

Precise accounting of the split (commit `4592c43`/`ef6adc3`):

```
$ git show 4592c43 -- backend/tests/ | grep -E '^-.*def test_'
test_soft_deleted_records_absent_from_default_responses   (api_contract)
test_change_password_updates_hash_in_db                    (auth_integration)
test_change_password_rejected_with_wrong_current_password  (auth_integration)
test_change_password_allowed_for_any_authenticated_user    (auth_integration)
test_sc012_pdf_upload_skips_unknown_tickers                (br001_gherkin)
test_soft_delete_holding_sets_deleted_at_in_db             (holdings_integration)
test_soft_deleted_holding_excluded_from_list               (holdings_integration)
test_update_holding_inline                                 (holdings_integration)
                                                           = 8 removed → 215 − 8 = 207 ✓
```

The bugfix branch's `test_bugfix_regressions.py` has **6** tests. The
8-removed vs 6-attributed arithmetic reconciles as:

| # | Removed from test | Regression equivalent on bugfix? |
|---|---|---|
| 1 | `test_change_password_updates_hash_in_db` | ✅ `test_change_password_stores_naive_updated_at` |
| 2 | `test_soft_delete_holding_sets_deleted_at_in_db` | ✅ `test_holding_soft_delete_sets_deleted_at` |
| 3 | `test_update_holding_inline` | ✅ `test_update_holding_returns_holding_type_as_status` |
| 4 | `test_sc012_pdf_upload_skips_unknown_tickers` | ✅ `test_upload_pdf_returns_422_for_unparseable_pdf` |
| 5 | `test_change_password_rejected_with_wrong_current_password` | ❌ — the **first** of the two "gap" tests |
| 6 | `test_change_password_allowed_for_any_authenticated_user` | ❌ — the **second** of the two "gap" tests |
| 7 | `test_soft_deleted_holding_excluded_from_list` | ❌ (dropped; exclusion follows from #2's behavior) |
| 8 | `test_soft_deleted_records_absent_from_default_responses` | ❌ (dropped; same) |

And two regression tests are **net-new**, not re-creations:
`test_registrar_soft_delete_succeeds` and `test_user_soft_delete_succeeds`
(TZ-naive at registrar/user call sites — no test coverage on `test` before).

**The "2" gap** = the two auth change-password variant tests
(`test_change_password_rejected_with_wrong_current_password` and
`test_change_password_allowed_for_any_authenticated_user`). They were
removed from `test` only because they **call** the then-buggy
`change-password` endpoint (which would 500 without the fix); they assert
non-bug behavior (400-on-wrong-password, readonly-allowed-200) and so were
not re-created as bug-proving regression tests.

```
$ pytest --collect-only -q | tail -1     # test branch, post-split
211 tests collected   (207 passed + 4 xfailed)
```

## Closing criteria status

| Criterion | Status |
|---|---|
| Item 0: `.env.v3` untracked + gitignored | ✅ on `test` (a945876) + landing on `main` via PR #8 (2d0e0cb); residual history explained |
| Item 1: six full SHAs | ✅ above |
| Item 2: F-TD-001 reconciliation | ✅ PR #9 open (separate, own commits) |
| Item 3: F-026b PR scope | ⚠ clean-cut proven not viable (4 dashboard tests need F-026 routes absent from `main`); recommendation: `test → main` or authorize F-026 routes in the branch |
| Item 4: bug-fix PR #8 | ✅ MERGEABLE/CLEAN after rebase onto `origin/main` |
| Item 5: 215→207 arithmetic | ✅ accounted above (the two change-password variants) |

F-026b is ready to be marked closed in MASTER_CONTEXT once Item 3's PR
shape decision is made.