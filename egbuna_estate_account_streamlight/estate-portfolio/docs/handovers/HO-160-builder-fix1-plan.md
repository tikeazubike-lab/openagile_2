# HO-160 fix round 1 — plan (spec F-026c §9 A-1..A-7)

Files in scope: backend/scripts/import_registrar_research.py,
backend/tests/unit/test_import_registrar_research.py,
backend/tests/integration/test_import_registrar_research.py.

- [ ] Step 1 — RED unit tests (commit `test(f-026c): ...`)
      A-1, A-2, A-3 (x2: fill rule + second plan empty), A-4, A-5,
      A-6/AC-16 (parametrised base + ghost snapshot; merged+firm company),
      A-7/AC-17 (4 CLI tests with fake engine/session).
      Existing assertions touched (A-4/A-7 only):
        * test_ac7_head_office... sort_order 1 -> 20
        * test_field_sort_orders... min(rest) 20 -> 30, min(rest2) 10 -> 20
        * test_ac1_refuses_to_run_without_database_url argv + `--undo-out -`
        * test_apply_without_confirm_db... argv + `--undo-out -`
- [ ] Step 2 — implement, in order (commit `fix(f-026c): ...`)
      1. A-6: `_WorkCopy` working copy + `apply_ops_to_snapshot`,
         planner reads/updates it, derived link/value helpers (drop stale index sets).
      2. A-1 merge reactivate, A-2 Ensure role, A-3 fill rule, A-4 sort base,
         A-5 normalise trailing slash.
      3. A-7: `--undo-out <path|->` required with --apply, `_write_undo`
         inside the transaction before COMMIT, stdout markers, remove
         `_write_undo_file`/`_runs_dir`.
- [ ] Step 3 — integration (commit `test(f-026c): ...`)
      AC-1 calls `_run_preview` (seed committed on its own engine + cleanup in
      finally, because the preview needs its own fresh read-only transaction);
      AC-13 round-trips the record to_json -> json -> from_json.
- [ ] Step 4 — full unit suite, paste raw summary line.
- [ ] Report: SHAs, raw summaries, changed assertions.

Environment: python
/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python
Iterate: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none <python> -m pytest tests/unit/test_import_registrar_research.py -q -p no:cacheprovider
Baseline: 47 passed.
