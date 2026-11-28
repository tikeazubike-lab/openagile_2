Continue HO-160 fix round 1. Spec: `.context/feature-specs/F-026c-registrar-research-import.md` §9 (A-1..A-7, AC-16, AC-17).
Your plan from the last run: `docs/handovers/HO-160-builder-fix1-plan.md`. Your previous brief: `docs/handovers/HO-160-brief-builder-fix1.md`.

STATE (do not redo):
- Step 1 DONE: `2b13721c1e36b4201218ae83d1c7c3cd4fa8468c` (RED tests). Do not change those tests.
- Your half-finished A-6 refactor of `backend/scripts/import_registrar_research.py` is committed as
  `0f024f855f9543da6f45e8772d3176f8e5822a07`. Unit state now: 28 failed, 32 passed. 24 failures are one error:
  `AttributeError: '_Planner' object has no attribute 'active_to_key'` (a reference left from the old index sets).
  The other 4 are A-7 (`--undo-out` not added yet, `_write_undo` missing).

DO NOT query documentation, Context7 or the web. Do not read files outside this worktree. Spend no time re-planning.

WORK, in this order, committing after each:
1. Finish A-6 so the working-copy planner has no references to the removed index sets. Then A-1..A-5.
   Run the unit file; commit `fix(f-026c): A-1..A-6 ...` once those tests pass.
2. A-7: `--undo-out <path|->` required with `--apply`; `_write_undo(record, dest)` called inside the transaction
   before COMMIT; `-` prints between `=== F026C UNDO JSON BEGIN ===` / `=== F026C UNDO JSON END ===`;
   a writer exception rolls back and exits non-zero. Remove `_write_undo_file` / `_runs_dir`. Commit `fix(f-026c): A-7 ...`.
3. Integration file fixes (AC-1 calls the real preview entry; AC-13 round-trips to_json -> from_json). Do NOT run them. Commit `test(f-026c): ...`.
4. Full unit suite from backend/:
   `DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python -m pytest tests/unit -q -p no:cacheprovider`
   Paste the raw summary line.

Commit messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`.
REPORT: full 40-char SHAs, raw summary line, any assertion you changed and why.
