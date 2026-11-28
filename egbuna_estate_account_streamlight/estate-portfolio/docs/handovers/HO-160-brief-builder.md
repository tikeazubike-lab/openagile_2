Implement spec `.context/feature-specs/F-026c-registrar-research-import.md` (read it fully first; it is the contract).
Working directory is the EPM project dir. HO: HO-160.

ENVIRONMENT (given; do not search for it, do not scan the filesystem, do not install anything):
- Python: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python
- Unit test command, run from backend/:
  DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none <python above> -m pytest tests/unit -q -p no:cacheprovider
- Baseline before your work: all unit tests green (130 passed, 4 xfailed or thereabouts). Report the exact line.
- Do NOT run tests/integration and do NOT connect to any real database. The orchestrator runs integration tests.
- Skip planning ledgers and skills; go straight to the steps.

FILES IN SCOPE (nothing else):
- backend/scripts/import_registrar_research.py (new)
- backend/tests/unit/test_import_registrar_research.py (new)
- backend/tests/integration/test_import_registrar_research.py (new)
- backend/tests/fixtures/registrar_research_sample.md (new, small hand-made sample in the same format, for unit tests)
Forbidden: any change under backend/app/, alembic/, the frontend, docs/registrars/registrars_contact_details_final.md.

DESIGN CONSTRAINTS (so it can be tested against a real DB inside a rollback):
- Pure layer: `parse_research(path) -> Research` (reads the single ```json block), `classify(client) -> "firm"|"weak"`,
  label/normalisation helpers, and `build_plan(research, snapshot, resolution_table) -> Plan`, where `snapshot` is a
  plain dataclass of the current rows. No DB access in this layer.
- DB layer: `async load_snapshot(session)`, `async apply_plan(session, plan) -> UndoRecord`,
  `async undo(session, undo_record)`. These take an `AsyncSession`, never commit, and never create engines.
  The CLI `main()` owns the engine, the transaction, `SET TRANSACTION READ ONLY` for preview, commit/rollback,
  `--confirm-db` (compare with `select current_database()`), and writing the undo JSON file.
- The §3 resolution table is a module constant `RESOLUTION_TABLE` and an argument to `build_plan`, so tests pass their
  own ids. Verify the table against the snapshot (spec §3) inside `build_plan`, and raise `ResolutionError` on mismatch.
- Use SQLAlchemy Core or ORM with `app.models` (Registrar, RegistrarContactField, CompanyRegistrar, Company,
  RegistrarRequirement). Soft-delete = set `deleted_at`. Never `DELETE`.
- Never print DATABASE_URL. Print the plan as readable lines plus a final counts block:
  registrars created / merged / soft-deleted / renamed, fields added, legacy columns filled, links created /
  reactivated / soft-deleted, companies.registrar_id changed, held back (weak), unmatched, without_contact_record.

STEPS (commit after each, message prefix `feat(f-026c):` or `test(f-026c):`, ending with the line
`Co-Authored-By: OpenCode <noreply@opencode.ai>`):
1. RED: write the unit tests for AC-5, AC-6, AC-7, AC-10, AC-11 and AC-14 (name check), plus the label/normalisation
   rules in spec §4.1.4 and §4.2, against the sample fixture. Commit them failing (import error counts as RED).
2. Write the integration test file for AC-1..AC-4, AC-8, AC-9, AC-12, AC-13, AC-15, using the existing
   `tests/integration/conftest.py` rollback session fixture. Build your own fixture registrars and companies with
   your own resolution table. Skip only if the database is unreachable. Do not run it. Commit.
3. Implement the script until the unit tests pass. Commit.
4. Run the full unit suite and paste the raw summary line.

Every test carries `# Spec: F-026c-registrar-research-import.md | AC-N`.

REPORT: the commit SHAs (full 40 chars), the raw unit summary line before and after, anything in the spec you could
not do or had to interpret, and the exact CLI usage.
