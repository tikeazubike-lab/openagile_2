HO-160: implement spec F-026c §13 (R-13.1..R-13.5, AC-25..AC-27). This is fix round 1 for §12.
Spec: `.context/feature-specs/F-026c-registrar-research-import.md` §13 (read §12 for context only).
Auditor findings with file:line: `docs/handovers/HO-160-registrar-research-import.md` §4.10.
DO NOT query documentation, Context7 or the web. Do not read files outside this worktree. No DB, no containers, do not run tests/integration.
Iterate, from backend/:
  DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python -m pytest tests/unit/test_import_registrar_research.py -q -p no:cacheprovider -x
STEPS (commit after each; messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`):
1. RED unit tests for AC-25 (use the REAL meristem and unity research entries; parse them from docs/registrars/registrars_contact_details_final.md,
   or copy their contact blocks into a fixture), AC-26 (on the existing `_snapshot()` shape), AC-27, R-13.3 (a soft-deleted holding still aborts),
   and R-13.5. Prove RED. Commit.
2. Implement R-13.1..R-13.5 in backend/scripts/import_registrar_research.py and fix the D-6 comment (audit #5). Commit.
3. Integration: extend test_ac24 so its research has contact data for meristem/unity and asserts a second plan = 0 ops (do not run it). Commit.
4. Full unit suite; paste the raw summary line.
REPORT: 40-char SHAs, raw summary line, any existing assertion changed and why.
