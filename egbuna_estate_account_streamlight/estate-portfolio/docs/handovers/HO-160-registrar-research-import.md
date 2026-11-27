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
