# backend/tests/integration/test_import_registrar_research.py
"""
F-026c — integration tests for the registrar research import (real Postgres).

Covered acceptance criteria: AC-1, AC-2, AC-3, AC-4, AC-8, AC-9, AC-12, AC-13,
AC-15 (spec `.context/feature-specs/F-026c-registrar-research-import.md`).

Every test runs inside the `db_session` rollback fixture from
tests/integration/conftest.py: the fixture registrars/companies are inserted
uncommitted and the whole test is rolled back at teardown, so epm_test is left
exactly as it was.

The tests build their own fixture rows and their own resolution table (spec §3),
against the hand-made sample file tests/fixtures/registrar_research_sample.md,
so nothing here depends on production ids. All three layers of the script are
exercised for real:
  * pure  — parse_research() (from the file path) + build_plan()
  * db    — load_snapshot() / apply_plan() / undo() against the live tables
  * cli   — the read-only preview transaction (SET TRANSACTION READ ONLY as the
            first statement, then a write that must fail with SQLSTATE 25006)

The CLI's own engine path is deliberately *not* run: `--apply` commits on its
own connection, which the rollback fixture forbids (AC-15 instead proves the
transaction boundary by failing mid-apply inside a savepoint).

Trace on every test:
  # Spec: F-026c-registrar-research-import.md | AC-N
"""
import json
import os
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from scripts.import_registrar_research import (
    ResolutionEntry,
    UpdateRegistrarOp,
    apply_plan,
    build_plan,
    format_plan,
    load_snapshot,
    parse_research,
    undo,
)
from app.models import (
    Company,
    CompanyRegistrar,
    Registrar,
    RegistrarContactField,
    RegistrarDocument,
    RegistrarRequirement,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "registrar_research_sample.md"

# Fixture registrar names. The resolution table's §3 name check requires the
# canonical id (and each duplicate) to contain the slug's first word: "alpha".
K_NAME = "F026c Alpha Test Registrars Ltd"
D1_NAME = "F026c Alpha Old Test Registrars"
D2_NAME = "F026c Alpha Second Test Registrars"
X_NAME = "F026c Unrelated Test Registrars"
Y_NAME = "F026c Co-Registrar Test Registrars"
NEW_NAME = "F026c Newbie Test Registrars Ltd"


# ─── fixture data ──────────────────────────────────────────────────────────────

def _research():
    """The hand-made sample file, parsed through the real parser."""
    return parse_research(FIXTURE)


def _table(ids: dict) -> dict:
    """The test's own resolution table (spec F-026c §3)."""
    return {
        "alpha": ResolutionEntry(
            slug="alpha", canonical=ids["k"], duplicates=(ids["d1"], ids["d2"]),
            final_name=K_NAME,
        ),
        "newbies": ResolutionEntry(
            slug="newbies", canonical=None, duplicates=(), final_name=NEW_NAME,
        ),
    }


async def _seed(session: AsyncSession) -> dict:
    """Fixture registrars, companies and links for one test (rolled back)."""
    k = Registrar(name=K_NAME, email="legacy@alpha.example", phone="01 999 9900",
                  jurisdiction="nigeria", status="active")
    d1 = Registrar(name=D1_NAME, response_rating=4, jurisdiction="nigeria",
                   status="active")
    d2 = Registrar(name=D2_NAME, jurisdiction="nigeria", status="active")
    x = Registrar(name=X_NAME, jurisdiction="nigeria", status="active")
    y = Registrar(name=Y_NAME, jurisdiction="nigeria", status="active")
    session.add_all([k, d1, d2, x, y])
    await session.flush()

    # AC-3: the duplicate carries an `other` contact field + two requirements
    # with their documents — all of it has to end up on the canonical registrar.
    fax = RegistrarContactField(
        registrar_id=d1.id, field_type="other", field_value="Fax 01-999 9901",
        label="fax", sort_order=1,
    )
    session.add(fax)
    reqs = []
    for order, title in enumerate(["Quarterly returns", "Annual audit pack"], start=1):
        req = RegistrarRequirement(
            registrar_id=d1.id, task_name=title, document_title=title,
            is_required=True, sort_order=order,
        )
        session.add(req)
        reqs.append(req)
    await session.flush()

    docs = []
    for number, req in enumerate(reqs, start=1):
        doc = RegistrarDocument(
            registrar_requirement_id=req.id,
            file_name=f"alpha-doc-{number}.pdf",
            file_path=f"/uploads/registrar_documents/alpha-{number}.pdf",
            file_size=1024, mime_type="application/pdf", status="submitted",
        )
        session.add(doc)
        docs.append(doc)

    alpha_co = Company(ticker="ALPHA", name="F026 Alpha Foods Plc",
                       sector="CONSUMER GOODS", status="listed", registrar_id=x.id)
    weak_co = Company(ticker="WEAKCO", name="F026 Weak Bank Plc",
                      sector="BANKS", status="listed", registrar_id=d1.id)
    unv_co = Company(ticker="UNVCO", name="F026 Unverified Plc",
                     sector="BANKS", status="listed", registrar_id=d2.id)
    newbie_co = Company(ticker="NEWBIE", name="F026 Newbie Plc",
                        sector="BANKS", status="listed", registrar_id=None)
    session.add_all([alpha_co, weak_co, unv_co, newbie_co])
    await session.flush()

    session.add_all([
        # AC-2: the canonical and the duplicate both link ALPHA — the duplicate's
        # row must be soft-deleted, never re-pointed (UNIQUE company, registrar).
        CompanyRegistrar(company_id=alpha_co.id, registrar_id=k.id, role="primary"),
        CompanyRegistrar(company_id=alpha_co.id, registrar_id=d1.id, role="primary"),
        # AC-8: ALPHA's current primary is unrelated registrar X (firm mapping).
        CompanyRegistrar(company_id=alpha_co.id, registrar_id=x.id, role="primary"),
        # AC-9: ... plus a co_registrar link that must survive untouched.
        CompanyRegistrar(company_id=alpha_co.id, registrar_id=y.id, role="co_registrar"),
        # merge re-point (no row on the canonical yet)
        CompanyRegistrar(company_id=weak_co.id, registrar_id=d1.id, role="primary"),
        CompanyRegistrar(company_id=unv_co.id, registrar_id=d2.id, role="primary"),
        # NEWBIE has no link at all: the firm mapping creates one
    ])
    await session.flush()

    return {
        "k": k.id, "d1": d1.id, "d2": d2.id, "x": x.id, "y": y.id,
        "alpha_co": alpha_co.id, "weak_co": weak_co.id, "unv_co": unv_co.id,
        "newbie_co": newbie_co.id,
        "fax_field": fax.id,
        "reqs": [r.id for r in reqs],
        "docs": [d.id for d in docs],
    }


# ─── helpers ───────────────────────────────────────────────────────────────────

async def _dump(session: AsyncSession) -> dict:
    """Every column of every table this feature touches, keyed by table name."""
    out = {}
    for table in (Registrar.__table__, RegistrarContactField.__table__,
                  CompanyRegistrar.__table__, Company.__table__,
                  RegistrarRequirement.__table__):
        rows = await session.execute(select(table).order_by(table.c.id))
        out[table.name] = [dict(row._mapping) for row in rows]
    return out


async def _apply(session: AsyncSession, table: dict):
    """load → plan → apply, the sequence the CLI runs."""
    snapshot = await load_snapshot(session)
    plan = build_plan(_research(), snapshot, table)
    await apply_plan(session, plan)
    await session.flush()
    return plan


def _sqlstate(exc) -> str | None:
    """SQLSTATE of a DBAPI/asyncpg error, whichever attribute carries it."""
    candidates = [
        getattr(exc, "sqlstate", None),
        getattr(exc, "pgcode", None),
        getattr(exc, "code", None),
        getattr(getattr(exc, "orig", None), "sqlstate", None),
        getattr(getattr(exc, "orig", None), "pgcode", None),
    ]
    for value in candidates:
        if isinstance(value, str) and len(value) == 5:
            return value
    return None


def _is_read_only_rejection(exc) -> bool:
    """True when the write was refused because the transaction is read-only."""
    if _sqlstate(exc) == "25006":
        return True
    text_blob = f"{type(exc).__name__} {exc!r}".lower()
    return "read-only" in text_blob or "readonly" in text_blob


def _read_only_engine():
    """A second connection to the same database (same env vars as conftest)."""
    url = (
        f"postgresql+asyncpg://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}"
        f"/{os.environ['DB_NAME']}"
    )
    return create_async_engine(url, poolclass=NullPool)


async def _active_links(session, company_id):
    return (await session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == company_id,
            CompanyRegistrar.deleted_at.is_(None),
        )
    )).scalars().all()


async def _registrar(session, registrar_id) -> Registrar:
    return (await session.execute(
        select(Registrar).where(Registrar.id == registrar_id)
    )).scalar_one()


# ─── AC-1: read-only preview ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac1_preview_prints_the_plan_and_counts_and_changes_nothing(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-1
    """Preview runs, no row changes, and the read-only transaction the CLI
    opens rejects every write with SQLSTATE 25006."""
    ids = await _seed(db_session)

    before = await _dump(db_session)
    snapshot = await load_snapshot(db_session)
    plan = build_plan(_research(), snapshot, _table(ids))
    out = format_plan(plan)
    after = await _dump(db_session)

    assert before == after, "preview changed rows"
    # plan + counts are printed
    assert "==" in out and "registrar" in out
    assert "== counts ==" in out
    assert "registrars: created=" in out
    assert "held back (weak)=" in out
    assert "companies.registrar_id changed=" in out

    # The CLI preview transaction: SET TRANSACTION READ ONLY is its first
    # statement, so any write attempt fails as read-only.
    engine = _read_only_engine()
    try:
        async with engine.connect() as conn:
            async with conn.begin():
                await conn.execute(text("SET TRANSACTION READ ONLY"))
                with pytest.raises(Exception) as excinfo:
                    await conn.execute(
                        text("UPDATE registrars SET name = 'blocked' WHERE id = :i"),
                        {"i": ids["k"]},
                    )
                assert _is_read_only_rejection(excinfo.value), (
                    f"write refused for the wrong reason: {excinfo.value!r}"
                )
    finally:
        await engine.dispose()


# ─── AC-2: duplicate merge ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac2_duplicates_merge_into_the_canonical_without_unique_violation(
        db_session: AsyncSession, user_http_client):
    # Spec: F-026c-registrar-research-import.md | AC-2
    """Both duplicates are soft-deleted, every link ends up on the canonical
    (one row per company — no unique violation) and the list endpoint shows the
    registrar exactly once."""
    ids = await _seed(db_session)
    await _apply(db_session, _table(ids))

    # duplicates soft-deleted, canonical untouched
    for duplicate in (ids["d1"], ids["d2"]):
        row = await _registrar(db_session, duplicate)
        assert row.deleted_at is not None, f"duplicate #{duplicate} still active"
    assert (await _registrar(db_session, ids["k"])).deleted_at is None

    # links point at the canonical; exactly one active row per company
    for company_id in (ids["alpha_co"], ids["weak_co"], ids["unv_co"]):
        links = await _active_links(db_session, company_id)
        primary = [l for l in links if l.role == "primary"]
        assert len(primary) == 1, f"company #{company_id} has {len(primary)} primaries"
        assert primary[0].registrar_id == ids["k"]
    # the duplicate's own row for ALPHA was soft-deleted (UNIQUE pair)
    all_alpha = (await db_session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == ids["alpha_co"],
            CompanyRegistrar.registrar_id == ids["d1"],
        )
    )).scalars().all()
    assert len(all_alpha) == 1 and all_alpha[0].deleted_at is not None

    # the list endpoint shows the canonical registrar exactly once
    response = await user_http_client.get("/api/v1/registrars")
    assert response.status_code == 200
    names = [row["name"] for row in response.json()["data"]]
    assert names.count(K_NAME) == 1
    assert D1_NAME not in names
    assert D2_NAME not in names


# ─── AC-3: rating, fields, requirements + documents ────────────────────────────

@pytest.mark.asyncio
async def test_ac3_rating_field_requirements_and_documents_move_to_the_canonical(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-3
    """The duplicate's response rating and `other` field land on the canonical,
    its requirements move with their documents, and the stored file paths do not
    change (downloads read registrar_documents.file_path, F5)."""
    ids = await _seed(db_session)
    await _apply(db_session, _table(ids))

    canonical = await _registrar(db_session, ids["k"])
    assert canonical.response_rating == 4

    fields = (await db_session.execute(
        select(RegistrarContactField).where(
            RegistrarContactField.registrar_id == ids["k"],
            RegistrarContactField.deleted_at.is_(None),
        )
    )).scalars().all()
    moved = [f for f in fields if f.field_type == "other"
             and f.field_value == "Fax 01-999 9901"]
    assert len(moved) == 1 and moved[0].label == "fax"

    for req_id in ids["reqs"]:
        req = (await db_session.execute(
            select(RegistrarRequirement).where(RegistrarRequirement.id == req_id)
        )).scalar_one()
        assert req.registrar_id == ids["k"]
        assert req.deleted_at is None

    for doc_id in ids["docs"]:
        doc = (await db_session.execute(
            select(RegistrarDocument).where(RegistrarDocument.id == doc_id)
        )).scalar_one()
        assert doc.registrar_requirement_id in ids["reqs"]
        assert doc.deleted_at is None
        # F5: the download route uses the stored path — it must be untouched
        assert doc.file_path == f"/uploads/registrar_documents/alpha-{ids['docs'].index(doc_id) + 1}.pdf"


# ─── AC-4: hand-entered legacy values ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac4_legacy_columns_become_entered_manually_fields(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-4
    """A registrar with hand-entered legacy email/phone and no contact fields
    gets those values as fields labelled "Entered manually"; the legacy columns
    themselves are never changed."""
    ids = await _seed(db_session)
    await _apply(db_session, _table(ids))

    canonical = await _registrar(db_session, ids["k"])
    # legacy columns unchanged (never overwritten)
    assert canonical.email == "legacy@alpha.example"
    assert canonical.phone == "01 999 9900"

    fields = (await db_session.execute(
        select(RegistrarContactField).where(
            RegistrarContactField.registrar_id == ids["k"],
            RegistrarContactField.deleted_at.is_(None),
        )
    )).scalars().all()
    manual = {(f.field_type, f.field_value) for f in fields if f.label == "Entered manually"}
    assert ("email", "legacy@alpha.example") in manual
    assert ("phone", "01 999 9900") in manual
    # and the researched values are visible on the page too
    visible = {(f.field_type, f.field_value) for f in fields}
    assert ("email", "desk@alpha.example") in visible
    assert ("phone", "+2341000000001") in visible


# ─── AC-8 / AC-9: company links ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac8_firm_mapping_makes_the_canonical_the_only_primary(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-8
    """ALPHA (firmly mapped, previously primary of unrelated registrar X) ends
    up with exactly one active primary — the canonical registrar — and
    companies.registrar_id points at the canonical too (the detail page reads
    that FK, F1)."""
    ids = await _seed(db_session)
    await _apply(db_session, _table(ids))

    links = await _active_links(db_session, ids["alpha_co"])
    primary = [l for l in links if l.role == "primary"]
    assert len(primary) == 1
    assert primary[0].registrar_id == ids["k"]

    # X's old primary row is soft-deleted
    old = (await db_session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == ids["alpha_co"],
            CompanyRegistrar.registrar_id == ids["x"],
        )
    )).scalars().all()
    assert len(old) == 1 and old[0].deleted_at is not None

    # companies.registrar_id changed (C appears on K's detail page)
    alpha = (await db_session.execute(
        select(Company).where(Company.id == ids["alpha_co"])
    )).scalar_one()
    assert alpha.registrar_id == ids["k"]


@pytest.mark.asyncio
async def test_ac9_co_registrar_link_is_untouched(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-9
    """The co_registrar link of the same company survives the firm mapping."""
    ids = await _seed(db_session)
    await _apply(db_session, _table(ids))

    rows = (await db_session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == ids["alpha_co"],
            CompanyRegistrar.registrar_id == ids["y"],
        )
    )).scalars().all()
    assert len(rows) == 1
    assert rows[0].role == "co_registrar"
    assert rows[0].deleted_at is None


# ─── AC-12: idempotency ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac12_second_apply_plans_zero_changes(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-12
    """After an apply, applying again plans nothing and writes nothing."""
    ids = await _seed(db_session)
    table = _table(ids)
    await _apply(db_session, table)

    snapshot = await load_snapshot(db_session)
    plan_again = build_plan(_research(), snapshot, table)
    assert plan_again.ops == []
    assert all(value == 0 for value in plan_again.counts.values()), plan_again.counts
    assert plan_again.report_counts["held_back"] == 2     # WEAKCO, UNVCO
    assert plan_again.report_counts["unmatched"] == 2     # GHOST, no ticker

    before = await _dump(db_session)
    await apply_plan(db_session, plan_again)
    await db_session.flush()
    assert await _dump(db_session) == before


# ─── AC-13: undo ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac13_undo_restores_every_touched_row(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-13
    """Undo restores the previous values of every touched row, soft-deletes the
    rows the apply inserted and reactivates the merged duplicates."""
    ids = await _seed(db_session)
    table = _table(ids)
    before = await _dump(db_session)

    snapshot = await load_snapshot(db_session)
    plan = build_plan(_research(), snapshot, table)
    record = await apply_plan(db_session, plan)
    await db_session.flush()
    assert await _dump(db_session) != before, "apply changed nothing — test is vacuous"
    assert record.inserted_rows, "apply inserted no rows"

    await undo(db_session, record)
    await db_session.flush()
    after = await _dump(db_session)

    for table_name, rows in before.items():
        after_by_id = {row["id"]: row for row in after[table_name]}
        for row in rows:
            assert after_by_id[row["id"]] == row, (
                f"{table_name}#{row['id']} does not match its pre-apply state"
            )

    for table_name, row_id in record.inserted_rows:
        row = next(r for r in after[table_name] if r["id"] == row_id)
        assert row["deleted_at"] is not None, (
            f"inserted {table_name}#{row_id} survived undo"
        )

    # duplicates are active again
    for duplicate in (ids["d1"], ids["d2"]):
        assert (await _registrar(db_session, duplicate)).deleted_at is None


# ─── AC-15: mid-apply failure ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ac15_error_mid_apply_rolls_back_everything(db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-15
    """An error halfway through the apply rolls the transaction back: nothing
    that the earlier ops wrote survives."""
    ids = await _seed(db_session)
    table = _table(ids)
    before = await _dump(db_session)

    snapshot = await load_snapshot(db_session)
    plan = build_plan(_research(), snapshot, table)
    # A statement that fails on every row: registrars.phone is VARCHAR(50).
    plan.ops.append(UpdateRegistrarOp(
        registrar_key=ids["k"], changes={"phone": "X" * 600},
    ))

    with pytest.raises(Exception):
        async with db_session.begin_nested():       # the apply transaction
            await apply_plan(db_session, plan)
        pytest.fail("the failing statement did not raise")

    await db_session.flush()
    assert await _dump(db_session) == before, "a partial apply survived the rollback"
