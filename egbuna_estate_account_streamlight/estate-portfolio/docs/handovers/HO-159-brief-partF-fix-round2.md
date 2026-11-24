Execute Part F below (Parts A-E are done). Working directory is the EPM project dir.

ENVIRONMENT (given; do not search for it, do not scan the filesystem, do not install anything):
- Unit test command, run from backend/: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python -m pytest tests/unit -q -p no:cacheprovider
- Current state: 1 failed (the intentional RED AC-6 test), 127 passed, 4 xfailed.
- Skip planning ledgers and skills; go straight to F1, commit, F2, commit, F3, commit.


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
