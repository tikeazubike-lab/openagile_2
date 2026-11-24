== role=builder model=opencode-go/mimo-v2.6-flash branch=feature/f-026-dashboard-and-f-026b-reminders log=/tmp/claude-1000/-home-zubbyik-openagile-2-egbuna-estate-account-streamlight-estate-portfolio/4ef0d904-59f3-41e9-94e8-eb9be42dd925/scratchpad/runs/20261123-132137-builder.jsonl
== denied tool calls:
== errors:
== new commits:
  4a2d5f3c833ab065a470d849633573f56e290eae test(f-026b): RED — real send_email except path leaks traceback text; plus AC-5 ReminderLog check (E3, Aud 4/5)
  6b74198fbd42dce4e8f4ab785d71d0356bbd84b7 test(f-026b): scope cron AC-1/AC-3 assertions to the fixture's own requirement (E2, Aud 2/3)
  2d8c3fe336453f0a91fe83d1322891c6d91c7a24 fix(f-026): count completed requirements, not documents, in dashboard_summary (E1, Aud 7)
== uncommitted:
== final report:
| E2 | `6b74198fbd42dce4e8f4ab785d71d0356bbd84b7` | test(f-026b): scope cron AC-1/AC-3 assertions to the fixture's own requirement (E2, Aud 2/3) |
| E3 | `4a2d5f3c833ab065a470d849633573f56e290eae` | test(f-026b): RED — real send_email except path leaks traceback text; plus AC-5 ReminderLog check (E3, Aud 4/5) |

Working tree clean; nothing pushed; no containers/DB/secrets touched.

## What changed

**E1** — `backend/app/routers/registrars.py` + tests
- `dashboard_summary` now counts `count(distinct(registrar_documents.registrar_requirement_id))` (status `completed`, `deleted_at IS NULL`), then clamps `completed_reqs = min(completed_reqs, total_reqs)` — so `completed_requirements ≤ total_requirements` and `completion_pct ≤ 100` by construction (docs can outlive a soft-deleted requirement).
- New `backend/tests/unit/test_registrars_dashboard_summary.py` (3 tests, fake async session, no DB): pins the compiled SQL shape (must contain `count(distinct(registrar_documents.registrar_requirement_id))`, must NOT contain `count(registrar_documents.id)`, status + soft-delete filters present), the clamp (raw 5 > total 3 → 3 and `100.0`), and the zero-dataset case. Trace: `# Spec: F-026-registrar-dashboard.md | AC-1 | Then counts and completion_pct match the data.`
- New integration test in `tests/integration/test_registrars_dashboard.py`: a second completed doc on `req1` must keep counts at 2/3 = 66.7% (old code would say 3/3 = 100%) — **marked `skip`: "NOT RUN — requires an epm_test run (Part E1); builder does not touch databases"**; `py_compile`-checked only.

**E2** — `tests/integration/test_registrar_reminder_cron.py`
- AC-1: replaced always-true `assert "failed=" in caplog.text` with a parsed assertion on the logged count: `re.search(r"completed: sent=\d+, skipped=\d+, failed=(\d+)", caplog.text)` → `failed >= 1`. The `reminder_log` assertions were already scoped to the fixture's `req_id`; kept. `mock_smtp.assert_not_called()` kept — it encodes "transmits nothing" and is deterministic (blank config bails before SMTP for every requirement).
- AC-3: replaced global `mock_send.call_count == 1` with calls filtered by the fixture's `document_title` in the subject → exactly 1, `"Overdue"` asserted on that call; `reminder_log` rows remain scoped to `req_id`.

**E3** — `tests/unit/test_reminders_router.py`
- AC-5: removed the tautological `mock_db.add.call_count == 0` (the handler never references `session` at all). Replaced with `patch("app.routers.registrars.ReminderLog")` + `assert_not_called()` — direct proof that no `ReminderLog(...)` is constructed on the test-send path.
- AC-6: new `test_test_send_real_smtp_exception_returns_502_without_leaking` — **real** `send_email`/`send_test_email`, only `app.services.email.smtplib.SMTP` patched to raise `_LeakySMTPError` whose message contains `/home/zubbyik/.secrets/smtp.env` and `Traceback`; asserts 502 and that the body contains neither `Traceback`, the fake path, the exception class path, nor the module path.

## Raw test output (dead `DATABASE_URL`, from `backend/`)

Baseline before my changes:
```
124 passed, 4 xfailed, 16 warnings in 7.61s
```
After E1:
```
127 passed, 4 xfailed, 16 warnings in 7.68s
```
Final (after E1+E2+E3):
```
FAILED tests/unit/test_reminders_router.py::test_test_send_real_smtp_exception_returns_502_without_leaking
1 failed, 127 passed, 4 xfailed, 16 warnings in 7.73s
```
The single failure is the E3 AC-6 real-path test, **intentional RED** (see escalation).

## Escalation — the RED test proves a real AC-6 bug (ruling needed)

`email.py:61` sanitizes with `error_msg = str(e)[:200]` — **truncation only, no scrubbing**. I verified directly: a 146-char message containing `Traceback (most recent call last):` + the fake path passes through whole into the 502 body:
```
DETAIL REPR: 'Traceback (most recent call last):\n  File "/home/zubbyik/.secrets/smtp.env", line 12, ...'
contains Traceback: True / contains fake path: True
```
So the test as specified by E3 fails against current code — AC-6 ("no raw stack trace exposed") is violated for leaky exception messages; the old AC-6 test never caught it because it mocked `send_email` (Aud 5's exact point).

**I did not fix `email.py`**: E3 scope is `backend/tests/` (`registrars.py` is "E1 only"), this brief carries no app-code carve-out, and the sanitizer design is your call. Options:
- **(a) minimal**: strip `Traceback`/`File "`/frame lines from `error_msg`, keep truncation;
- **(b) stronger**: return a generic `"SMTP send failed — see server logs"` detail; the full error already goes to `logger.error` server-side;
- **(c)** accept as-is and weaken the test — not recommended, contradicts AC-6.

The test XPASSes the moment either fix lands (then just drop the RED wording from the commit narrative).

## What was NOT done

- **E4**: untouched — pre-existing commits `f5757e9`, `8676c33`, `a3d15d3` were already on the branch when I started.
- **Integration tests not run** (E1's new test, E2's edited AC-1/AC-3 tests): no DB/container access per rules. E1's is marked `skip: NOT RUN`; E2's are `py_compile`-checked. Same open item already flagged in the PR (needs an `epm_test` run).
- **`registrar_health` block** (`registrars.py` ~:244-255 after my edit): same document-counting pattern (`reg_completed >= reg_req_count` counts documents, so 2 completed docs on req A + 0 on req B mislabels the registrar "complete"). Outside E1's cited range (:183-226), so left alone — flag if you want it fixed.
- **Old AC-6 mocked test** still contains `assert mock_db.add.call_count == 0` (line ~137) — the same tautology Aud 4 named for AC-5; the brief only named AC-5, so left in place.
- One transparency note: the E1 query-shape assertion initially expected `count(DISTINCT …)` but SQLAlchemy renders `count(distinct(…))` — the assertion pins the actual rendering (it still fails against the old `count(registrar_documents.id)` code).
