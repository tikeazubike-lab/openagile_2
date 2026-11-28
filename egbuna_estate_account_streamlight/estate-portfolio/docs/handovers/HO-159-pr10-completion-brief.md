# HO-159 — PR #10 completion brief (Architect → Builder)

| Field | Value |
|---|---|
| From / To | Claude Code (architect/orchestrator) → OpenCode builder (Part A: deepseek-v4.1-flash, run before the model change; Part B: mimo-v2.6-pro) |
| Date | 2026-11-23 |
| Branch | `feature/f-026-dashboard-and-f-026b-reminders` (PR #10), base head `ca5ff5c792fa354bc1501a77e428558a40fa98f7` |
| Specs | `.context/feature-specs/F-026-email-reminder-infrastructure.md` (F-026b), `.context/feature-specs/F-026-registrar-dashboard.md` (F-026) |
| HO block | HO-159..HO-208 approved by Zubbyik 2026-11-23 |
| Trigger | Auditor verdict DEVIATED on PR #10 (findings 4 and 5) |

## Architect rulings (no builder action needed)
- **R-1 Route paths.** Backend stays at `/api/v1/admin/reminders/test-send` and `/api/v1/admin/reminders/log`.
  The locked rule "admin routes at /settings/*, never /admin/*" is about **frontend pages**: HO-024 itself
  defines backend endpoints under `/api/v1/admin/holdings`, and F-016 ships `/api/v1/admin/users`.
  Auditor finding 3 is closed as a false positive. The UI lives under `/settings/` (Part B).
- **R-2 Spec order.** The F-026 and F-026b spec-after-code breaches are ratified exceptions (Product Owner, 2026-11-23),
  recorded in `F-026-registrar-dashboard.md` §8, for the v4.11 Decision Log.

## Part A — backend tests (role: builder)
Scope: test files only under `backend/tests/`. **Do not change application code** unless a test proves a bug;
if so, make the smallest fix and say so explicitly in the report.

Add tests for the F-026b acceptance criteria that are missing or mock-only:
| AC | Test to add | Where |
|---|---|---|
| AC-1 | cron run with SMTP config missing/invalid → logs error, does not raise, sends nothing | next to the existing cron tests (find `test_registrar_reminder_cron.py`) |
| AC-3 | requirement with `due_date` in the past → one send, `reminder_type == "overdue"` | same file |
| AC-5 | `POST /api/v1/admin/reminders/test-send` as admin, SMTP send mocked OK → 200 `{"status":"sent",...}`, and no `reminder_log` write | router-level test, follow `backend/tests/unit/test_admin_users.py` (`dependency_overrides`) |
| AC-6 | same endpoint, SMTP send raises → 502, body has no traceback text | same |
| AC-8 | non-admin user → 403 on both endpoints | same |
Each test carries a trace comment: `# Spec: F-026-email-reminder-infrastructure.md | AC-N | Then ...`.

Order: write the tests and commit (RED or GREEN is fine, since the code already exists; report which).
If any fails because of a real bug, fix it in a separate commit.

Run unit tests with a dead database URL so nothing can reach production:
`cd backend && DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none python -m pytest tests/unit -q`
Paste the raw summary line. Do not run `tests/integration`.

## Part B — frontend (role: frontend)
Scope: `estate-portfolio-manager/src/` only.
1. Port the F-026b settings page that already exists on branch `test`, **byte-for-byte**:
   `git show test:egbuna_estate_account_streamlight/estate-portfolio/estate-portfolio-manager/src/routes/_app.settings.registrars.tsx > estate-portfolio-manager/src/routes/_app.settings.registrars.tsx`
2. Add the sidebar entry the same way `test` has it: in `src/components/layout/Sidebar.tsx`,
   `{ to: "/settings/registrars", label: "Registrars", icon: ClipboardList }` (import `ClipboardList` from lucide-react if missing).
   Compare with `git show test:.../Sidebar.tsx` and copy only that entry and import.
3. Regenerate `src/routeTree.gen.ts` with the project's TanStack Router generator
   (`npx @tanstack/router-cli generate`, or whatever `package.json` / vite config uses). Do not hand-edit it.
4. Verify: `npx tsc --noEmit -p tsconfig.json` shows **no new errors** in the files you touched
   (14 errors already exist elsewhere; list any in your files), and `npm run test` (vitest) raw summary.
   Do not run `npm run build`.
5. Do **not** build `RegistrarsDashboard` (F-026 §5). That waits for the task 3 decision.

## Forbidden (enforced by permissions; do not look for workarounds)
Pushing, history rewrite, containers, database clients, Alembic upgrade/downgrade/stamp, reading `.env*`,
editing `opencode.json` / `.claude/` / `.git/`, network fetches, money as float, inline row editing.

## Report back
What changed, raw test output, full 40-char SHAs, what was NOT done, anything you had to decide.

## Part C — F-026 registrar dashboard UI (role: frontend) — added 2026-11-23
Product Owner decision: **rebuild from spec** (no recovery from the running container).
Spec: `.context/feature-specs/F-026-registrar-dashboard.md` §3 (API contract) and §5 (frontend).
Scope: `estate-portfolio-manager/src/` only.

1. Create `src/components/registrars/RegistrarsDashboard.tsx`:
   - Data: `GET /api/v1/registrars/dashboard-summary` and
     `GET /api/v1/registrar-requirements/global-tracker?page=&page_size=20` via `@tanstack/react-query`,
     using the same fetch/auth pattern as `src/routes/_app.settings.registrars.tsx`
     (responses may be wrapped in the `{data, meta, error}` envelope — unwrap the way that file does).
   - Summary tiles (`components/ui/card`): completion % (`completion_pct`, show 1 dp + `%`),
     total / completed / pending requirements, registrar health (complete / attention / no data).
   - "Needs attention" list from `top_action_items` (task, document, registrar, due date or "—").
   - Unmapped companies: count + up to 20 tickers/names.
   - Global tracker: TanStack Table, server-side pagination (`page`, `total_pages`), columns:
     task, document, registrar, status badge, due date, latest document file + status.
     Follow the table pattern in `src/routes/_app.companies.tsx`.
   - Loading (`components/ui/skeleton`) and error states. Read-only: no inline edit controls.
2. Render it at the top of `/registrars` from `src/components/registrars/RegistrarsLayout.tsx`
   (above the existing list/details layout). Keep the existing behaviour unchanged.
3. Test: `src/components/registrars/__tests__/RegistrarsDashboard.test.tsx` (vitest + Testing Library),
   mocking `fetch` for both endpoints; assert tiles, an attention item, and a tracker row render (AT-026 AC-7).
   Trace comment: `// Spec: F-026-registrar-dashboard.md | AC-7 | Then ...`.
   Note: 4 of 9 existing vitest files fail to import because `@testing-library/jest-dom` is missing
   (AUDIT R10). Do not install packages; if your test needs jest-dom matchers, use plain
   `expect(...).toBeTruthy()` / `getByText` instead, and report it.
4. Verify: `npx tsc --noEmit -p tsconfig.json` — no errors in files you touched; `npx vitest run` raw summary.
5. Commit; report SHAs. Do not touch backend code.
6. Architect ruling on Part B escalation 2 (fix it, in a separate commit): in
   `src/routes/_app.settings.registrars.tsx`, unwrap the `{data, meta, error}` envelope for both
   test-send (`recipient`, `status`, `detail`) and the reminder log, check `res.ok` on the log query and
   show an error state instead of "No reminders sent yet." on 4xx/5xx. Prefer the existing helper in
   `src/api/queries` (`fetchApiEnvelope`) if it fits. Byte-for-byte parity with `test` no longer applies.
   Rename the admin sidebar label to "Reminder Settings" to avoid two "Registrars" entries.

## Part D — make the new frontend tests run under `npm run test` (role: builder) — added 2026-11-23
Architect ruling on Part C escalation C1: tests that the project runner skips do not count.
Scope: `estate-portfolio-manager/vitest.config.ts` only, plus deleting the scratch file below.

1. In `estate-portfolio-manager/vitest.config.ts`:
   - add `"src/**/__tests__/**/*.test.ts"` and `"src/**/__tests__/**/*.test.tsx"` to `test.include`
     (keep the existing `tests/**` entries);
   - add `resolve.alias` so `@` maps to `./src` (same as `vite.config.ts`; use
     `fileURLToPath(new URL("./src", import.meta.url))` or `path.resolve(__dirname, "src")`).
2. Delete the untracked scratch file `vitest.ho159-scratch.config.ts` at the worktree root
   (two levels above the EPM dir: `../../vitest.ho159-scratch.config.ts`). Do not commit it.
3. Run `cd estate-portfolio-manager && npx vitest run` and paste the raw summary. Expected: the 3 new
   `src/**/__tests__` files (12 tests) now run and pass; the 4 pre-existing jest-dom import failures remain
   (do not install packages, do not touch those files).
4. Commit: `test(config): collect src/**/__tests__ and add @ alias in vitest (HO-159 Part D)`.

## Review responses (architect, 2026-11-23)
Auditor (Claude, fresh context): **ALIGNED**, conditional on AC-1/AC-3 integration runs.
Reviewer (DeepSeek v4 Pro, advisory): **SHIP**. Every finding is answered below.

| Source # | Finding | Response |
|---|---|---|
| Aud 7 / Rev 1 | `completion_pct` counts completed documents, not requirements; can exceed 100% | **Accepted**, fix in Part E1 |
| Aud 2 | cron AC-1/AC-3 tests assert global `call_count == 1`; brittle on shared epm_test | **Accepted**, Part E2 |
| Aud 3 | `"failed=" in caplog.text` always true | **Accepted**, Part E2 |
| Aud 5 / Rev 2 | AC-6 mocks the sanitizer; the real `except` path in email.py is untested | **Accepted**, Part E3 |
| Aud 4 / Rev 3 | AC-5 `session.add` assertion is tautological | **Accepted**, Part E3 (replace, don't pretend) |
| Aud 6 | two mislabelled trace comments | **Accepted**, Part E4 |
| Rev 5 | dashboard duplicates `fetchApiEnvelope` | **Accepted**, Part E4 |
| Rev 6 | inert `manualPagination`/`pageCount` table config | **Accepted**, Part E4 |
| Aud 1 / Rev 4 | regenerated routeTree also routes `/claims` and `/companies/$id` | **Escalated to Zubbyik** at PR review: the generated tree is the canonical output and equals `test`'s, so those pages already ship from `test`. Not reverted |
| Aud 8 | nested scroll column in RegistrarsLayout | **Rejected for now**: behaviour kept, covered by a test; cosmetic |
| Aud (unverified) | AC-1/AC-3 integration tests not run | **Open**: needs an epm_test run, flagged in the PR |

## Part E — fix round 1
### E1–E3 (role: builder) — scope `backend/app/routers/registrars.py` (E1 only) and `backend/tests/`
- **E1** In `dashboard_summary` (`registrars.py` ~:183-226), count **requirements** that have at least one
  non-deleted document with `status == "completed"`, i.e. `count(distinct RegistrarDocument.requirement_id)`
  or the as-built equivalent, using the relationship that already exists. Keep `completion_pct` ≤ 100 and
  `completed_requirements` ≤ `total_requirements`. Add a unit test with a mocked session that pins the new
  query shape, and an integration test (two completed docs on one requirement → counted once), marked as
  not run. Trace: `# Spec: F-026-registrar-dashboard.md | AC-1 | Then ...`.
- **E2** In `backend/tests/integration/test_registrar_reminder_cron.py`: in the new AC-1/AC-3 tests, assert only
  on calls and `reminder_log` rows for **the fixture's own requirement id**, not global counts. Replace the
  `"failed=" in caplog.text` check with an assertion on the logged count or drop it (the reminder_log row
  carries the AC).
- **E3** In `backend/tests/unit/test_reminders_router.py`:
  - AC-6: add a test that uses the **real** `send_email`/`send_test_email` with `smtplib.SMTP` patched to raise
    an exception whose message contains a fake path and the word `Traceback`; assert 502 and that the body
    contains neither the exception class path nor `Traceback`.
  - AC-5: remove the tautological `mock_db.add.call_count == 0` assertion. If `send_test_email` can be
    patched to prove no `ReminderLog(...)` is constructed, assert that; otherwise leave a comment saying
    "no DB write path exists in the handler" and say so in the report.
- Run unit tests with the dead DATABASE_URL and paste the raw summary.
### E4 (role: frontend) — scope `estate-portfolio-manager/src/`
- Reuse `fetchApiEnvelope` from `src/api/queries` in `RegistrarsDashboard.tsx` instead of the local helper,
  if behaviour is identical (keep the tests green).
- Remove the inert `manualPagination`/`pageCount` options (or wire them properly; prefer removal).
- Fix the trace comments: `RegistrarsDashboard.test.tsx` ~:200 (the cookie test is not F-026 AC-5) and
  `src/routes/__tests__/_app.settings.registrars.test.tsx` ~:54 (log-query error state is not F-026b AC-6).
  Label them with the real AC or as "supporting" tests.
- Run `npx vitest run` and the `tsc` check; paste raw summaries.

## Part F — fix round 2 (role: builder) — architect rulings on the Part E escalations
- **F1 — AC-6 leak (accepted, ruling: option b).** `backend/app/services/email.py` (~:60-63): on exception,
  log the full error server-side (`logger.error(..., exc_info=True)` is fine) and return a **generic** detail:
  `{"status": "failed", "detail": "SMTP send failed — see server logs"}`. Never put `str(e)` in the response.
  Apply the same to any other path in that file that returns exception text. Keep the reminder cron's
  `reminder_log.error_detail` server-side only (it is not returned by any endpoint except the admin log; if
  the admin log returns `error_detail`, keep it, as it is admin-only and already truncated). The RED test from
  `4a2d5f3c833ab065a470d849633573f56e290eae` must turn GREEN without being weakened.
- **F2 — `registrar_health` (accepted).** In `dashboard_summary` (`registrars.py` ~:244-255), a registrar is
  "complete" only when **every** one of its requirements has at least one completed, non-deleted document.
  Same distinct-requirement counting as E1. Add a unit test (mocked session, pins the query shape) and an
  integration test (2 completed docs on req A, 0 on req B → registrar is "attention", not "complete"),
  marked not run. Trace: `# Spec: F-026-registrar-dashboard.md | AC-1 | Then ...`.
- **F3 — tautology (accepted).** Remove `assert mock_db.add.call_count == 0` from the old mocked AC-6 test
  in `test_reminders_router.py` (or replace it with a meaningful assertion), same reasoning as AC-5.
- Scope: `backend/app/services/email.py`, `backend/app/routers/registrars.py` (F2 block only), `backend/tests/`.
- Commit F1, F2 and F3 separately. Final unit run must be fully green.

## Final audit of fix rounds (26e82958..958100ef) and closing rulings
Auditor: **ALIGNED (conditional)**: nothing blocks the push. Unit run: 130 passed, 4 xfailed.
The fix-round limit (2) is reached, so the remaining minor items are follow-ups, not a third round.

| # | Finding | Ruling |
|---|---|---|
| 1 | `completed_requirements` doesn't exclude docs on soft-deleted requirements. The clamp caps it, but the % can be overstated | **Follow-up FU-1**: reuse F2's live-requirement subquery in E1 |
| 2 | `reminder_log.error_detail` now always holds the generic message | **Accepted as is.** Security (AC-6) takes priority over convenience. Full errors stay in the server log (`exc_info=True`). The F1 text "keep error_detail" is superseded by this ruling |
| 3 | `SMTP_PORT` int-parse sits outside the try. A bad value gives a 500 on test-send and crashes the cron (AC-1). This predates PR #10 (ca956a56) | **Follow-up FU-2**: parse inside the guarded config check and treat a bad value as "config incomplete" |
| 4 | New E1/F2 integration tests are unconditionally skipped | **Follow-up FU-3**: replace with a skip only when epm_test is unreachable, as part of the epm_test run decision |

Open for Zubbyik at PR review:
- **(a) Integration tests:** they have not been run, and that needs a decision on epm_test access.
- **(b) Regenerated route tree:** it also exposes `/claims` and `/companies/$id`, with the same tree as `test`.

Follow-ups FU-1..FU-3 get their own HO from the approved block after PR #10 merges.

## Part G — tabs on /registrars (role: frontend) — 2026-11-24
**Why:** Playwright on testdrive (1440x900, logged in) showed the registrar list squeezed to 32px and its
scroll area to 0px under the 804px dashboard; the 36 registrars could not be seen or clicked. Auditor
finding Aud 8 (nested scroll column) flagged this and was wrongly rejected as cosmetic; that rejection
is withdrawn. Product Owner chose tabs (spec F-026 §9, AC-7 reworded, AC-8 and AC-9 new).

Scope: `estate-portfolio-manager/src/components/registrars/RegistrarsLayout.tsx` and
`estate-portfolio-manager/src/components/registrars/__tests__/RegistrarsLayout.test.tsx` only.
- **G1 (RED first):** rewrite `RegistrarsLayout.test.tsx`:
  - AC-8: on render, a tab named "Registrars" is selected, the list heading "Registrars" and
    "Select a registrar to view details" are shown, "Registrar Dashboard" is NOT in the document, and
    `fetch` was NOT called for `dashboard-summary` or `global-tracker`.
  - AC-7: after activating the "Dashboard" tab, "Registrar Dashboard" and the tile value ("62.5%") render.
    Radix tabs activate on `mouseDown` (left button) or keyboard, not on `click`; `@testing-library/user-event`
    is NOT installed, so use `fireEvent.mouseDown(tab, { button: 0 })` (or focus + keyDown). Do not add packages.
  - Trace comments: `// Spec: F-026-registrar-dashboard.md | AC-8 | Then ...` / `AC-7`.
  - Run it and confirm it fails against the current layout; commit the RED test on its own.
- **G2 (GREEN):** in `RegistrarsLayout.tsx` use the existing `@/components/ui/tabs`
  (`Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`), `defaultValue="registrars"`, local state only:
  - outer container: `flex h-[calc(100vh-4rem)] flex-col bg-background`, no `overflow-y-auto` on it;
  - `TabsList` row: `shrink-0`, with a small top/left padding;
  - Registrars `TabsContent`: `flex-1 min-h-0 mt-0` and inside it the ORIGINAL pre-F-026 list/details layout
    (left panel `md:w-[320px] border-r flex flex-col`, right panel `flex-1 overflow-y-auto bg-muted/20`), filling
    `h-full`; no fixed `h-[calc(...)]` inside the tab;
  - Dashboard `TabsContent`: `flex-1 min-h-0 overflow-y-auto mt-0`, renders `<RegistrarsDashboard />`.
    Radix unmounts inactive content by default; keep that (no `forceMount`), so the dashboard queries run on demand.
  - Keep `selectedId` state in the layout so the selected registrar survives a tab switch.
- Do not touch `RegistrarsDashboard.tsx`, `RegistrarList.tsx`, backend, routes or config.
- Run `npx vitest run` and `npx tsc --noEmit -p tsconfig.json`; paste raw summaries. Expected baseline:
  4 files fail on missing jest-dom (pre-existing); tsc errors only in Navbar, claims, companies.$id, price-history.
- Commit G1 and G2 separately. Do not push.
- AC-9 (real layout at three viewports) is verified by the orchestrator with Playwright on a real build; not your job.

### Part G review responses (architect, 2026-11-24)
Built: G1 `8247c1029ce4fda7a54e959d6b05d78bbe4e7838` (RED, verified failing on the pre-G2 layout by the auditor),
G2 `04fb8910a21a2ded230901db184a221d83d8fc8d`. Orchestrator re-run: vitest `Test Files 4 failed | 8 passed (12)`,
`Tests 32 passed (32)` (4 = pre-existing jest-dom); tsc 13 errors, only Navbar/claims/companies.$id/price-history.
**AC-9 (Playwright, real local build of 04fb891, live data, 2026-11-24): PASS** at 1280x720 / 1440x900 / 1920x1080:
list top 124px; list height 612/792/972px; scroll area 547/727/907px; 36 cards; dashboard not rendered and
0 dashboard requests before the tab opens; first card opens details; Dashboard tab shows tiles; selection kept.
Auditor (fresh context): **ALIGNED**, mutation-tested (forceMount and defaultValue="dashboard" both break AC-8).
Reviewer (DeepSeek v4 Pro, advisory): **SHIP**.

| Source # | Finding | Response |
|---|---|---|
| Aud 1 | tab bar uses margins, spans full width with centred triggers | **Accepted as is.** Cosmetic; confirmed in screenshots, readable. Product Owner can request a restyle |
| Aud 2 | no unit test for selection kept across tab switch | **Accepted as is.** Covered by the AC-9 Playwright run; not a spec AC |
| Aud 3 / Rev 3 | below md: stacked list can crowd details; `h-full` inside a flex item | **Accepted as is.** Byte-identical to pre-F-026 mobile behaviour; `h-full` verified working at three viewports |
| Aud 4 / Rev 2 | jsdom cannot assert heights | **Accepted.** That is why AC-9 exists and was run in a real browser |
| Rev 1 | AC-7 layout test checks tiles only, not tracker / no inline edit | **Accepted as is.** Tracker render and no-inline-edit are asserted in `RegistrarsDashboard.test.tsx` (:169, :252) |
| Rev 4 | "Registrars" is both the tab label and the list heading; no tablist aria-label | **Follow-up FU-4** (a11y nit), with FU-1..FU-3 |

No fix round needed. Aud 8 (Part E) rejection is withdrawn; the defect it predicted is fixed by Part G.
