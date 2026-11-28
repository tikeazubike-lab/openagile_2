HO-160: implement spec F-026c §12 (D-1..D-6, AC-19..AC-24). Branch `feature/f-026c2-po-decisions`.
Spec: `.context/feature-specs/F-026c-registrar-research-import.md` §12. Earlier sections still apply, except where §12 says it replaces them
(D-1 replaces A-9; D-5 replaces the §4.3 keep-both rule).
Production evidence for the shapes: `docs/handovers/HO-160-dups-report-2026-11-28.md`, `docs/handovers/HO-160-names-report-2026-11-28.md`.

DO NOT query documentation, Context7 or the web. Do not read files outside this worktree. No DB, no containers, do not run tests/integration.
Python: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python
Unit, from backend/: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none <python> -m pytest tests/unit -q -p no:cacheprovider

STEPS (commit after each; messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`):
1. RED unit tests for AC-19..AC-24 in backend/tests/unit/test_import_registrar_research.py. Update the existing A-9/AC-18 test to the
   D-1 behaviour (say so in the report). Prove RED, commit `test(f-026c): ...`.
2. Implement in backend/scripts/import_registrar_research.py, in this order:
   - D-2: add 15 to the greenwich duplicates in RESOLUTION_TABLE.
   - D-3: a TICKER_ALIASES = {"MEYER": "DNMEYER"} table, applied before ticker matching; abort if the target is not an active company.
   - D-1: the firm step retires all other active links of any role.
   - D-4: a DUPLICATE_COMPANIES table (keep → retire) as listed in §12. Soft-delete the company and its active links (new op type, undo restores).
     Abort at plan time if the snapshot shows holdings/transactions/dividends/registrar_documents for a retired row. Add those counts to
     load_snapshot (read-only selects). ACCESS is reported as FLAG, never retired.
   - D-5: the manual-wins rule per (registrar, type), with report lines `skipped (manual wins)`.
   - D-6: a PLACEHOLDER_CONTACTS table with the exact values; clear the legacy columns to NULL (undo restores); abort on mismatch.
   Keep A-1..A-8 behaviour (one op per row, distinct counts, undo before COMMIT). Commit `fix(f-026c): ...` (`feat` is fine).
3. In backend/tests/integration/test_import_registrar_research.py, change the AC-1 count expectation to `renamed=0`, and add integration
   tests for AC-19, AC-22 and AC-24 using the existing fixtures. Do not run them. Commit `test(f-026c): ...`.
4. Full unit suite; paste the raw summary line.
REPORT: 40-char SHAs, raw summary line, any existing assertion changed and why.
