HO-160 fix round 2 (the LAST round). Spec: `.context/feature-specs/F-026c-registrar-research-import.md` §10 (A-8, A-9, AC-16 restated, AC-18).
Auditor pass-2 findings with file:line: `docs/handovers/HO-160-registrar-research-import.md` §4.6. Evidence: `docs/handovers/HO-160-preview-prod-2026-11-28.md`.
State: HEAD includes your round-1 work (`2c86c653d62f5038db500be274cbc188438c7f18`); unit suite 191 passed, 4 xfailed.

DO NOT query documentation, Context7 or the web. Do not read files outside this worktree. Do not run tests/integration. No DB.
Python: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python
Unit, from backend/: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none <python> -m pytest tests/unit -q -p no:cacheprovider

STEPS (commit after each):
1. RED unit tests (`test(f-026c): ...`):
   - Extend the unit snapshot with: a company on duplicate D of K1 firmly mapped to K2 ≠ K1 (one with an active D link, one whose K1 row is soft-deleted);
     a second duplicate with notes merging into the same canonical; a company whose firm target K has an active co_registrar row.
   - A row-level `_touches` check: no (table, id) appears in two ops (merge + firm steps both counted). Every count = distinct rows.
   - AC-18: co_registrar-at-target company: no ops for it, listed as `held back (co_registrar at target)`.
   - Prove RED, commit.
2. Implement A-8 then A-9 in `backend/scripts/import_registrar_research.py` (`fix(f-026c): ...`). Simplest approach: before the merge
   step, compute the set of firm-mapped companies with their final target, and have the merge step skip their links and registrar_id;
   combine per-canonical registrar value merges into one op. Do not change behaviour outside A-8/A-9.
3. Full unit suite; paste the raw summary line.
Commit messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`.
REPORT: 40-char SHAs, raw summary line, any existing assertion changed and why.
