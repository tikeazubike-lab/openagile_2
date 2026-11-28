## F-026c: registrar research import (HO-160)

A one-off **data import script**. There are no app-code, schema or migration changes, and **nothing has been written to production**.
It imports `docs/registrars/registrars_contact_details_final.md` (sha256 `87ff3927…c6cc45ea9`) and does three things:
- adds contact fields
- merges 10 duplicate registrars into their canonical rows (soft delete only)
- rewrites company links from the file's firm mappings

The 13 low-confidence or UNVERIFIED mappings are **held back** (Product Owner decision).

- Spec: `.context/feature-specs/F-026c-registrar-research-import.md` (§3 resolution table, §4 rules, amendments in §9–§11)
- HO log and finding responses: `docs/handovers/HO-160-registrar-research-import.md`
- Script: `backend/scripts/import_registrar_research.py`
  - preview by default; `--apply --confirm-db estate_portfolio --undo-out <path|->`; `--undo FILE`

### Evidence
- Unit: `195 passed, 4 xfailed` (the xfails are the unrelated BUG-HOLD-DIVYIELD-001)
- Read-only production preview #3 (`transaction_read_only = on`): `docs/handovers/HO-160-preview-prod-2026-11-28-r2.md`
  - 7 registrars created, 10 merged, 3 renamed
  - 184 contact fields added
  - `registrar_id` changed on 132 companies (132 distinct); 100 links created, 54 soft-deleted, 19 repointed
  - 13 held back; 53 unmatched
- Auditor: 3 passes. Pass 3 is DEVIATED (narrow). Finding 1 was settled by a ruling (§11); gaps G-1 and G-2 do not occur in the current data.

### ⚠️ Not proven
- **The apply/undo SQL has not run on a real database.** The integration tests (`tests/integration/test_import_registrar_research.py`) exist but were not run, because running them against `epm_test` was not approved.
- The DeepSeek advisory review was stopped for low memory and not re-run.
- §11 precondition: before applying, confirm the single production `co_registrar` row is not on a duplicate registrar from §3.

### Before the production apply (Product Owner's go, spec §7)
1. `pg_dump` backup
2. `--apply --confirm-db estate_portfolio --undo-out -` inside the container
3. Commit the undo JSON (only from a run that exits 0)
4. Playwright check of the registrars page

Open questions:
- Run the integration tests on `epm_test`?
- Placeholder-looking hand contacts on Meristem and Unity
- Order of the "Entered manually" fields
- `opencode serve --service` keeps builder sessions alive after they are killed (HO-160 §4.7)

Stacked on #10 (`feature/f-026-dashboard-and-f-026b-reminders`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
