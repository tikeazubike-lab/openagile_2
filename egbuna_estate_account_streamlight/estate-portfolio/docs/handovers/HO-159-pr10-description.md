F-026 registrar dashboard and F-026b email reminders: backend, frontend, migrations and tests.

**Head:** `a2d004bba534a8c724ade21a34f2943895b1841a`. The full brief, rulings and review responses are in `docs/handovers/HO-159-pr10-completion-brief.md`.

## Since the first audit (DEVIATED)
That audit covered `0415599514a32773482dba2c40fd26deb8c46e3c..ca5ff5c792fa354bc1501a77e428558a40fa98f7`. The 27 commits after it close its findings:

- **Specs:** added the missing F-026 dashboard spec (retroactive). You ratified both spec-after-code exceptions (R-2).
- **Route paths:** backend admin paths stay at `/api/v1/admin/*`. The `/settings/*` rule covers frontend pages only, following the HO-024 and F-016 precedent (R-1).
- **F-026b frontend:** ported the `/settings/registrars` page from `test`, added a sidebar entry ("Reminder Settings") and regenerated the route tree.
- **F-026 frontend:** built `RegistrarsDashboard` on `/registrars`, with summary tiles, a needs-attention list, unmapped companies and a paginated global tracker.
- **Tests:** added F-026b AC-1, AC-3, AC-5, AC-6 and AC-8. `vitest.config.ts` now picks up `src/**/__tests__`; before this, `npm run test` silently skipped the new frontend tests.
- **Bugs found by review and fixed:**
  - "Sent to undefined" after a test send: the page did not unwrap the response envelope.
  - `completion_pct` counted documents instead of requirements, so it could exceed 100%.
  - `registrar_health` had the same counting bug.
  - **Security (AC-6):** test-send returned raw SMTP exception text, including traceback lines and paths, in its 502 response. It now returns a generic message, and the full error goes to the server log only.
  - Fixed `_app.companies.$id.tsx`, which would not parse.

## Reviews
| Review | Verdict |
|---|---|
| Auditor on the new work | ALIGNED |
| DeepSeek v4 Pro (advisory) | SHIP |
| Auditor on the fix rounds | ALIGNED (conditional) |

Every finding is answered in HO-159.

## Verified by the orchestrator (raw)
```
backend unit (dead DATABASE_URL):  130 passed, 4 xfailed
vitest:                            Test Files 4 failed | 8 passed (12), Tests 31 passed (31)
tsc --noEmit:                      13 errors, all in untouched files (Navbar, claims, companies.$id, price-history)
```
The 4 failing vitest files are not from this PR: they fail to import `@testing-library/jest-dom` (AUDIT R10).

## Needs your decision
1. **Integration tests have not run.** These are the cron AC-1/AC-3 tests and the E1/F2 dashboard tests. They need `epm_test` access.
2. **Two more pages go live.** The regenerated route tree also exposes `/claims` and `/companies/$id`. It matches `test`'s tree, but `/claims` has type errors.
3. **Deploy:** merging does not deploy anything. testdrive still runs the image built on 2026-07-19.

**Follow-ups after merge:**
- FU-1: also exclude soft-deleted requirements from the completion count.
- FU-2: make a bad `SMTP_PORT` value count as "config incomplete" instead of crashing.
- FU-3: make the integration-test skips conditional.

**Built by OpenCode agents:**
| Part | Agent |
|---|---|
| A (backend tests) | deepseek-v4.1-flash |
| B, C, E4 (frontend) | mimo-v2.6-pro |
| D, E1–E3, F (backend fixes) | mimo-v2.6-flash |

Orchestrated by Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
