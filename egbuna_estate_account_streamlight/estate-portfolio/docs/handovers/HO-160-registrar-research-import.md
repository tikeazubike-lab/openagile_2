# HO-160 — Registrar research import (F-026c)

| Field | Value |
|---|---|
| From / To | Claude Code (orchestrator/architect) → OpenCode builder; Product Owner at Gate 2 |
| Date | 2026-11-27 |
| Spec | `.context/feature-specs/F-026c-registrar-research-import.md` |
| Branch | `feature/f-026c-registrar-research-import`, base `bafd6b9540d83b9cbb7bef10eea6a91d9669a35f` (PR #10 head) |
| HO block | HO-159..HO-208 (approved 2026-11-23); HO-160 is the next unused number |

## 1. Session-start audit (2026-11-27, raw state)
- `origin/main` = `14068e76d20847282bbe32c60ec5345a15513e67` (PR #16 merged). Main tree on `test` at
  `c29932c86e0de64cbaa482bcbaeeb1bd23f9daf8`, equal to `origin/test`. Uncommitted in the main tree:
  `M .claude/orchestration/opencode.builder.json`; untracked `docs/registrars/`, `.context/MASTER_CONTEXT-v4.10-Update_package.md`,
  `priority_registrars.md`, `epm-claude-skills.tar.gz`, `swaks`, `.playwright-mcp/`.
- Open PRs: #10 (F-026 + F-026b, head `bafd6b9540d83b9cbb7bef10eea6a91d9669a35f`, MERGEABLE, no review yet), #9, #8.
- Production: `alembic_version = e1f2a3b4c5d6`; 36 registrar rows (none soft-deleted), 249 active companies,
  165 `company_registrars` rows (164 primary, 1 co_registrar).
- Open risks still standing from AUDIT-2026-11-21: R2 (running image has no reproducible source),
  R3/R5 (main behind test, main's Alembic chain broken), R8 (reminder cron runs from the main tree),
  R10 (conftest defaults to production). R1 remains an accepted risk (not acted on).
- ARCHITECT-TAKEOVER-001 task 7 ("no new feature work until tasks 5 and 6 are approved") has no
  recorded approval for tasks 5/6. This HO is a data import with no app-code, schema or migration change, started on the
  Product Owner's explicit instruction of 2026-11-27. Flagged for the Product Owner, not treated as a block.

## 2. Product Owner decisions (2026-11-27)
- Scope: option 3 — contacts, merge duplicates, rewrite company links from the file's mappings
  ("the file mapping was thoroughly researched before it was submitted").
- Low-confidence / UNVERIFIED mappings (13 matched today): **held back**, listed for one-by-one decision.

## 3. Architect rulings
- R-1 **Both link stores are written.** The detail page reads the legacy `companies.registrar_id`, so
  writing only `company_registrars` would leave the page unchanged (spec F1). The legacy column is not retired here.
- R-2 **Hand data is never overwritten**, and is copied into `contact_fields` so it stays visible (spec F2, §4.3).
- R-3 **No company is created**, and matching is by exact ticker only. This is the standing lesson from the
  HO-101..106 seed incident.
- R-4 **The preview is enforced by Postgres** (`SET TRANSACTION READ ONLY`), not by the script's own logic.
  Production apply needs the Product Owner's go after the preview is reviewed (spec §7).
- R-5 The canonical-id table in spec §3 is fixed from production ids. The script verifies the table and aborts on drift.

## 4. Work log
(appended as the loop runs: builder report, test output, auditor + reviewer findings and responses, SHAs)

### 4.1 Builder runs
- Run 1 (mimo-v2.6-flash, 50 min, timed out): step 1 only, `184c4580dcae60c72cd2d2fa5bee3d28562f6b97` (RED unit tests + fixture).
  ~20 min went on documentation lookups; the continuation brief answered those questions directly.
- Run 2 (55 min, timed out): integration tests `02ec830efc5ace7300c34277b2af412abb0f17dc`; the script was left uncommitted and
  committed unchanged by the orchestrator as `5e53a50a7f7330719780cd61d8c80a81a34dff57` (attributed to the builder). One test was written
  after the timeout and committed unchanged as `ddcf3a7077ddfd69765c966ed8a2cd9f449169c1`. The run-2 log was truncated, so
  `HO-160-report-builder-run2.md` is partial.
- Orchestrator code change (disclosed): `b76b66c158291b7fadab315148bd8b67ce5a56f8` adds one `CompanyRow(UNVCO)` to the unit snapshot.
  No assertion changed. The auditor confirmed this.
- Unit suite after run 2: `177 passed, 4 xfailed` (auditor run).

### 4.2 Production preview (Product Owner approved, read-only)
`HO-160-preview-prod-2026-11-27.md`: `transaction_read_only = on`, db `estate_portfolio`. Product Owner decision on integration tests
against epm_test: **not approved**, so apply/undo SQL is unproven on a real DB.

### 4.3 Auditor pass 1: DEVIATED. Responses
| # | Finding | Response |
|---|---|---|
| 1 | Duplicate ops inflate counts; stale "before" values | **Accepted**: spec A-6, fix round 1 |
| 2 | Undo file is written only after COMMIT; the relative path lands inside the container | **Accepted**: spec A-7 (`--undo-out`, written before COMMIT, stdout markers for container runs) |
| 3 | Integration tests not run; AC-1 test doesn't call the preview path; AC-13 doesn't round-trip JSON | **Partly accepted**: the tests are fixed in round 1. Running them needs the Product Owner's approval (declined so far) and is raised again at the PR |
| 4 | Merge leaves no active link when K's row is soft-deleted | **Accepted** (spec gap): A-1 |
| 5 | Reactivation doesn't set role='primary' | **Accepted**: A-2 |
| 6 | Idempotency depends on the data | **Accepted**: A-3 |
| 7 | Head office sort_order=1 ignores existing fields | **Accepted**: A-4 |
| 8 | Trailing-slash URL duplicates | **Accepted**: A-5 |
| 9 | Stale registrar in soft-delete line | **Accepted**: same fix as #1 |
| 10 | Process artefacts outside backend/ | **No action**: these are HO artefacts, by rule |

### 4.4 DeepSeek review
Dispatched, then **stopped by Claude Code because the host was low on memory** (llama-server + whisper-cli were using about 5.7 GB of 7.8 GB).
Not restarted without the Product Owner's go. Advisory only, so it does not block.

### 4.5 Fix round 1 (builder)
- Run 1b timed out mid-refactor; its work was committed unchanged as `0f024f855f9543da6f45e8772d3176f8e5822a07` (attributed to the builder).
- Continuation run produced `54c969ffd20f4b208ea181f9ceb05b8e8685e44e` (A-1..A-6), `9257580cadf5093fb3b758f4d988ab2b2f7b030d` (A-7),
  `2c86c653d62f5038db500be274cbc188438c7f18` (integration test fixes, not run). Unit suite: `191 passed, 4 xfailed`.
- **Anomaly:** the dispatch's final report came from an OpenCode session that said it saw a *second* builder writing the same
  worktree and stood down. Only one `opencode run` was dispatched. A long-running `opencode serve --service` (pid 885369, started
  2026-11-27 09:26, not started by this loop) also exists on the host. The commits match the brief and the auditor reviewed them;
  the source of the duplicate session is not established. Flagged for the Product Owner.
- Production preview #2 (read-only, approved): `HO-160-preview-prod-2026-11-28.md`. `registrar_id changed=138` vs 132 distinct.

### 4.6 Auditor pass 2: DEVIATED. Responses
| # | Finding | Response |
|---|---|---|
| 1 | Merged then firm-mapped company gets `registrar_id` changed twice (6 in prod) | **Accepted**: spec A-8, fix round 2 |
| 2 | 10 link rows repointed then soft-deleted; reactivate-then-delete reachable | **Accepted**: A-8 (row-level) |
| 3 | AC-16 tests lack the production shape | **Accepted**: AC-16 restated |
| 4 | `notes` changed by two ops when two duplicates have notes | **Accepted**: A-8 |
| 5 | co_registrar at the firm target leaves no active primary | **Accepted**, ruled A-9: hold the company back |
| 6 | AC-1 integration 25006 check uses its own transaction | **Accepted** as a nit: round 2 asserts on the preview's own session if cheap; otherwise it's left as is |
| 7 | A COMMIT failure leaves a stale undo record on stdout | **Accepted**: §7 note (only an exit-0 run yields an undo file) |
| 8 | Placeholder URL in a unit test trips the secrets grep | **No action**: a fake host with masked password |
Pass-1 #2, #4–#9 are confirmed fixed by the auditor.

### 4.7 Fix round 2 (builder)
- The first round-2 run was stopped by Claude Code because the host was low on memory (llama-server and whisper-cli). Its partial tests were committed as `e8b9682fc2966127c946062c88cf9ce28520b972`.
  The Product Owner then had Ollama and the Hermes gateway stopped and disabled.
- **The builder session kept working after its `opencode run` client was killed.** It committed `f3f33ce310da417d58ace20c494d1794abc9af1f` (02:00, RED tests) and
  `886eda2b026aae3b0c18d6797b6bae33ea0194b3` (02:08, A-8/A-9) with no `opencode run` process alive. The persistent `opencode serve --service` (pid 885369)
  is the likely host, which would also explain the "second builder" in §4.5 and the writes after each timeout. **So dispatch timeouts and kills do not stop the builder.**
  Flagged for the Product Owner; the service was not touched.
- The restart run found the work done. It proved RED against `886eda2^` (5 failed) and ran the suite: `195 passed, 4 xfailed`.
- Production preview #3 (read-only): `HO-160-preview-prod-2026-11-28-r2.md`. `registrar_id changed=132` (132 distinct), no link row in two ops, no co_registrar-at-target case.

### 4.8 Auditor pass 3: DEVIATED (narrow). Fix loop exhausted (2/2). Responses
| # | Finding | Response |
|---|---|---|
| 1 | `registrars` rows get 2–3 ops (rename + merge values + fill); AC-16's literal text says one op per row | **Ruled** (spec §11): A-8 covers the companies/link rows of the merge and firm steps. No column is written twice. No code change |
| 2 | An A-9 held-back company on a duplicate stays on the soft-deleted duplicate | **Accepted as known gap G-1**: zero A-9 cases in preview #3, so it can't happen today |
| 3 | A firm-mapped company's co_registrar link on a duplicate is left on the soft-deleted duplicate | **Accepted as known gap G-2**: an apply precondition (§11). My read-only check of the one prod co_registrar row was blocked by guard-bash (the inline script reads DATABASE_URL), and the guard was not bypassed |
| 4 | Firm step prints the old registrar_id without "#" | Nit, deferred |
| 5 | No counts line for A-9 hold-backs | Nit, deferred (0 in production) |
| 6 | A ticker firm-mapped under two registrars | Nit: none in the file (`in >1 registrar: []`) |
Pass-2 #1–#5 are confirmed fixed. RED proof was reproduced by the auditor. End-state probe on all three fixtures: no duplicate pairs, no multi-primary, no stale links/FKs, 2nd run = 0 ops.
