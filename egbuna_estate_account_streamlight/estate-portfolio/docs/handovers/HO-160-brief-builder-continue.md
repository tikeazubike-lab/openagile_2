Continue HO-160 (spec `.context/feature-specs/F-026c-registrar-research-import.md`, first brief `docs/handovers/HO-160-brief-builder.md`).
Step 1 is DONE: commit 184c4580dcae60c72cd2d2fa5bee3d28562f6b97 (RED unit tests + sample fixture). Do not rewrite those tests;
you may fix a test only if it contradicts the spec, and you must say so in the report.
The previous run timed out after spending ~20 minutes on documentation lookups. Do NOT query documentation, Context7 or the web.
The answers you need are below. Work straight through Steps 2, 3 and 4.

ENVIRONMENT (same as before):
- Python: /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/backend/.venv/bin/python
- Unit tests, from backend/: DATABASE_URL=postgresql+asyncpg://nobody@127.0.0.1:1/none <python> -m pytest tests/unit -q -p no:cacheprovider
- Do not run tests/integration. Do not connect to any real database.

SETTLED FACTS (do not research):
- Read-only preview: in PostgreSQL `SET TRANSACTION READ ONLY` must be the FIRST statement of the transaction (before any
  query). With SQLAlchemy async: `async with engine.connect() as conn: async with conn.begin(): await conn.execute(text("SET TRANSACTION READ ONLY"))`,
  then bind an `AsyncSession(bind=conn)` and load the snapshot. Any write then fails with SQLSTATE 25006.
- `select current_database()` returns the DB name for `--confirm-db`.
- `company_registrars` UNIQUE(company_id, registrar_id) also covers soft-deleted rows: reactivate, never insert a duplicate.

EXTRA REQUIREMENT (for running the preview inside the production container, where only stdin is available):
- Expose `async def cli(argv: list[str], research_text: str | None = None) -> int`. When `research_text` is given, parse it
  instead of reading `--research` (default path: docs/registrars/registrars_contact_details_final.md relative to the EPM dir).
- Do not use `__file__` at import time unless it exists (`globals().get("__file__")`): the module must import cleanly when piped
  to `python -` with cwd `/app` (where the `app` package lives).
- The entry point must be exactly:
  `if __name__ == "__main__" and not globals().get("_F026C_EMBEDDED"): sys.exit(asyncio.run(cli(sys.argv[1:])))`
- Add one unit test: `parse` via `research_text` gives the same result as via the path (sample fixture).

STEPS:
2. Integration test file `backend/tests/integration/test_import_registrar_research.py` (AC-1..AC-4, AC-8, AC-9, AC-12, AC-13, AC-15),
   using the `db_session` rollback fixture from tests/integration/conftest.py, with your own fixture rows and resolution table.
   Do not run it. Commit (`test(f-026c): ...`).
3. Implement `backend/scripts/import_registrar_research.py` until all unit tests pass. Commit (`feat(f-026c): ...`).
4. Run the full unit suite; paste the raw summary line.
Commit messages end with `Co-Authored-By: OpenCode <noreply@opencode.ai>`.

REPORT: full 40-char SHAs, raw unit summary line, any spec interpretation, exact CLI usage.
