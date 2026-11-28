Execute ONLY sub-part E4 of Part E below. E1-E3 are done by another agent; do not touch backend. Working directory is the EPM project dir.


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
