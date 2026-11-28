# HO-160 — integration tests on epm_test, 2026-11-28 (Product Owner approved)

Run inside estate_portfolio_v3 with DB_NAME/DATABASE_URL forced to epm_test (preflight shown first). Code at da89ea0c3e236810ea1409b27d47e59c25181d96.

```
PREFLIGHT current_database = epm_test
F........                                                                [100%]
=================================== FAILURES ===================================
_______ test_ac1_preview_prints_the_plan_and_counts_and_changes_nothing ________

db_session = <sqlalchemy.ext.asyncio.session.AsyncSession object at 0x772bfe3f84a0>
capsys = <_pytest.capture.CaptureFixture object at 0x772bfe3fa720>

    @pytest.mark.asyncio
    async def test_ac1_preview_prints_the_plan_and_counts_and_changes_nothing(
            db_session: AsyncSession, capsys):
        # Spec: F-026c-registrar-research-import.md | AC-1
        """The real preview entry ``_run_preview()`` runs against the fixture
        database: it prints the plan and the counts, changes no row, and the
        read-only transaction it opens rejects every write with SQLSTATE 25006."""
        engine = _read_only_engine()
        ids = None
        try:
            # the preview needs a transaction of its own, so it can only see
            # committed rows: seed here, and delete everything again in `finally`
            ids = await _commit_seed(engine)
    
            before = await _dump(db_session)
            rc = await _run_preview(engine, _research(), resolution_table=_table(ids))
            out = capsys.readouterr().out
            after = await _dump(db_session)
    
            assert rc == 0
            assert before == after, "preview changed rows"
            # plan + counts are printed (which also proves the §3 checks passed)
            assert "== registrar research import: plan ==" in out
            assert "== counts ==" in out
>           assert "registrars: created=1 merged=2 soft-deleted=2 renamed=1" in out
E           assert 'registrars: created=1 merged=2 soft-deleted=2 renamed=1' in "== registrar research import: plan ==\n  create registrar 'F026c Newbie Test Registrars Ltd' (slug newbies)\n  merge ... NOREC (No Record Co Plc) for Nowhere Registrars Limited — not on the SEC register on 2026-11-26, no company created\n"

tests/integration/test_import_registrar_research.py:309: AssertionError
=============================== warnings summary ===============================
../../usr/local/lib/python3.12/site-packages/passlib/utils/__init__.py:854
  /usr/local/lib/python3.12/site-packages/passlib/utils/__init__.py:854: DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13
    from crypt import crypt as _crypt

tests/integration/test_import_registrar_research.py::test_ac2_duplicates_merge_into_the_canonical_without_unique_violation
  /usr/local/lib/python3.12/site-packages/jose/jwt.py:311: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    now = timegm(datetime.utcnow().utctimetuple())

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==================================== PASSES ====================================
=========================== short test summary info ============================
PASSED tests/integration/test_import_registrar_research.py::test_ac2_duplicates_merge_into_the_canonical_without_unique_violation
PASSED tests/integration/test_import_registrar_research.py::test_ac3_rating_field_requirements_and_documents_move_to_the_canonical
PASSED tests/integration/test_import_registrar_research.py::test_ac4_legacy_columns_become_entered_manually_fields
PASSED tests/integration/test_import_registrar_research.py::test_ac8_firm_mapping_makes_the_canonical_the_only_primary
PASSED tests/integration/test_import_registrar_research.py::test_ac9_co_registrar_link_is_untouched
PASSED tests/integration/test_import_registrar_research.py::test_ac12_second_apply_plans_zero_changes
PASSED tests/integration/test_import_registrar_research.py::test_ac13_undo_restores_every_touched_row
PASSED tests/integration/test_import_registrar_research.py::test_ac15_error_mid_apply_rolls_back_everything
FAILED tests/integration/test_import_registrar_research.py::test_ac1_preview_prints_the_plan_and_counts_and_changes_nothing
1 failed, 8 passed, 2 warnings in 3.44s
```
