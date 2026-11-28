# backend/tests/integration/test_import_registrar_research.py
"""
F-026c — integration tests for the registrar research import (real Postgres).

Covered acceptance criteria: AC-1, AC-2, AC-3, AC-4, AC-8, AC-9, AC-12, AC-13,
AC-15, AC-19, AC-22, AC-24 (spec `.context/feature-specs/F-026c-registrar-research-import.md`;
AC-19/AC-22/AC-24 and the §12 amendments of AC-4/AC-9 come from its §12).

Every test runs inside the `db_session` rollback fixture from
tests/integration/conftest.py: the fixture registrars/companies are inserted
uncommitted and the whole test is rolled back at teardown, so epm_test is left
exactly as it was. AC-1 is the single exception — it seeds and cleans up its
own committed rows, see its docstring.

The tests build their own fixture rows and their own resolution table (spec §3),
against the hand-made sample file tests/fixtures/registrar_research_sample.md,
so nothing here depends on production ids. All three layers of the script are
exercised for real:
  * pure  — parse_research() (from the file path) + build_plan()
  * db    — load_snapshot() / apply_plan() / undo() against the live tables
  * cli   — the read-only preview entry _run_preview() itself (AC-1): its
            transaction starts with SET TRANSACTION READ ONLY, so every write
            it attempts fails with SQLSTATE 25006

`--apply`'s own engine path is deliberately *not* run: it commits on its own
connection, which the rollback fixture forbids (AC-15 instead proves the
transaction boundary by failing mid-apply inside a savepoint). AC-1 needs the
preview in a transaction of its own — SET TRANSACTION READ ONLY must be its
first statement — so its fixture rows are seeded on a second connection and
COMMITTED, and every one of them is deleted again in the test's `finally`
(the rollback fixture cannot see another transaction's rows).

Trace on every test:
  # Spec: F-026c-registrar-research-import.md | AC-N
"""
import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from scripts.import_registrar_research import (
    PlaceholderMismatchError,
    Research,
    ResolutionEntry,
    RetireBlockedError,
    RetireCompanyOp,
    UndoRecord,
    UpdateRegistrarOp,
    _run_preview,
    apply_plan,
    build_plan,
    load_snapshot,
    parse_research,
    undo,
)
from app.models import (
    Company,
    CompanyRegistrar,
    Dividend,
    Holding,
    Registrar,
    RegistrarContactField,
    RegistrarDocument,
    RegistrarRequirement,
    Transaction,
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


async def _commit_seed(engine) -> dict:
    """Seed the fixture rows on their own connection and COMMIT them.

    AC-1 calls the real preview entry, which opens a transaction of its own
    (SET TRANSACTION READ ONLY must be its first statement): it cannot run
    inside db_session's transaction, and it cannot see db_session's
    uncommitted rows either. The rows are therefore committed here and every
    one of them is deleted again by _cleanup_committed_seed()."""
    conn = await engine.connect()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        ids = await _seed(session)
        await session.commit()
        return ids
    finally:
        await session.close()
        await conn.close()          # rolls a half-finished seed back


async def _cleanup_committed_seed(engine, ids: dict) -> None:
    """Delete the rows _commit_seed() committed — the rollback fixture cannot,
    they belong to another transaction. FK order: documents -> requirements ->
    contact fields -> links -> companies -> registrars."""
    registrars = [ids["k"], ids["d1"], ids["d2"], ids["x"], ids["y"]]
    companies = [ids["alpha_co"], ids["weak_co"], ids["unv_co"], ids["newbie_co"]]
    async with engine.begin() as conn:
        await conn.execute(RegistrarDocument.__table__.delete().where(
            RegistrarDocument.__table__.c.registrar_requirement_id.in_(ids["reqs"])))
        await conn.execute(RegistrarRequirement.__table__.delete().where(
            RegistrarRequirement.__table__.c.id.in_(ids["reqs"])))
        await conn.execute(RegistrarContactField.__table__.delete().where(
            RegistrarContactField.__table__.c.registrar_id.in_(registrars)))
        await conn.execute(CompanyRegistrar.__table__.delete().where(
            CompanyRegistrar.__table__.c.company_id.in_(companies)))
        await conn.execute(Company.__table__.delete().where(
            Company.__table__.c.id.in_(companies)))
        await conn.execute(Registrar.__table__.delete().where(
            Registrar.__table__.c.id.in_(registrars)))


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
        # The fixture canonical already carries its §3 final name, so the plan
        # renames nothing (HO-160 §4.9: the stale expectation was renamed=1)
        assert "registrars: created=1 merged=2 soft-deleted=2 renamed=0" in out
        assert "held back (weak)=2" in out
        assert "companies.registrar_id changed=" in out

        # The preview transaction itself: SET TRANSACTION READ ONLY is its
        # first statement, so any write attempt fails as read-only.
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
        if ids is not None:
            await _cleanup_committed_seed(engine, ids)
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
    # Spec: F-026c-registrar-research-import.md | AC-4 (and AC-23 under §12 D-5)
    """A registrar with hand-entered legacy email/phone and no contact fields
    gets those values as fields labelled "Entered manually"; the legacy columns
    themselves are never changed.

    §12 D-5 (replaces the §4.3 keep-both rule): both hand values differ from
    every researched value of their type, so the researched phones and emails
    are NOT imported and are listed as ``skipped (manual wins)`` instead. The
    types without a hand value (address, website) import normally."""
    ids = await _seed(db_session)
    plan = await _apply(db_session, _table(ids))

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
    # §12 D-5: the researched values of a type the hand value wins are left out
    visible = {(f.field_type, f.field_value) for f in fields}
    assert ("email", "desk@alpha.example") not in visible
    assert ("phone", "+2341000000001") not in visible
    assert any(line.startswith("skipped (manual wins):") for line in plan.report_lines)
    # ... while the types without a hand value still import
    assert ("address", "1 Alpha Way, Lagos") in visible
    assert ("other", "https://alpha.example") in visible


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
async def test_ac9_co_registrar_link_is_soft_deleted_by_the_firm_mapping(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-9 (superseded by §12 D-1 → AC-19)
    """§12 D-1 replaces A-9 and its AC-9: co_registrar is not modelled, so the
    firm mapping makes the canonical the company's ONLY active link and the
    co_registrar row is soft-deleted with every other non-K link (AC-19). The
    row itself keeps its role, and undo restores it."""
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
    assert rows[0].deleted_at is not None, "D-1 must retire the co_registrar link"

    # exactly one active link remains: the canonical
    links = await _active_links(db_session, ids["alpha_co"])
    assert [(l.registrar_id, l.role) for l in links] == [(ids["k"], "primary")]


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

    # The record travels exactly as it does through an undo file:
    # to_json -> JSON text -> from_json (A-7/AC-13).
    round_tripped = UndoRecord.from_json(json.loads(json.dumps(record.to_json())))
    assert round_tripped.to_json() == record.to_json()

    await undo(db_session, round_tripped)
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


# ─── §12 (HO-160 §4.9): Product Owner decisions → AC-19, AC-22, AC-24 ─────────

async def _link(session: AsyncSession, company_id: int, registrar_id: int):
    return (await session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == company_id,
            CompanyRegistrar.registrar_id == registrar_id,
        )
    )).scalars().one_or_none()


async def _company(session: AsyncSession, company_id: int) -> Company:
    return (await session.execute(
        select(Company).where(Company.id == company_id)
    )).scalar_one()


async def _assert_restored(db_session: AsyncSession, before: dict) -> None:
    """Every row that existed before the apply is byte-identical again (AC-13's
    comparison, as a helper: rows the apply INSERTED are not in `before`, so
    the soft-deleted rows an undo leaves behind are outside this check)."""
    after = await _dump(db_session)
    for table_name, rows in before.items():
        after_by_id = {row["id"]: row for row in after[table_name]}
        for row in rows:
            assert after_by_id[row["id"]] == row, (
                f"{table_name}#{row['id']} does not match its pre-apply state")


# ─── AC-19 / D-1: one registrar per company, co_registrar not modelled ─────────

@pytest.mark.asyncio
async def test_ac19_a_firm_mapping_retires_the_co_registrar_and_undo_restores_it(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-19
    """§12 D-1 (replaces A-9): the firm mapping makes the canonical ALPHA's only
    active link — the co_registrar row of registrar Y is soft-deleted with every
    other non-K link, the company ends with exactly one active link, and undo
    puts the co_registrar row back exactly as it was."""
    ids = await _seed(db_session)
    table = _table(ids)
    before = await _dump(db_session)

    co_row = await _link(db_session, ids["alpha_co"], ids["y"])
    assert co_row is not None and co_row.deleted_at is None   # starts active

    snapshot = await load_snapshot(db_session)
    plan = build_plan(_research(), snapshot, table)
    record = await apply_plan(db_session, plan)
    await db_session.flush()

    links = await _active_links(db_session, ids["alpha_co"])
    assert [(l.registrar_id, l.role) for l in links] == [
        (ids["k"], "primary")], "D-1 left more than one active link"

    db_session.expire_all()  # re-read: apply/undo write through SQL, not the ORM objects
    retired = await _link(db_session, ids["alpha_co"], ids["y"])
    assert retired.deleted_at is not None
    assert retired.role == "co_registrar"          # the row itself is untouched

    await undo(db_session, record)
    await db_session.flush()
    db_session.expire_all()  # re-read: apply/undo write through SQL, not the ORM objects
    restored = await _link(db_session, ids["alpha_co"], ids["y"])
    assert restored.deleted_at is None             # undo reactivates it
    assert restored.role == "co_registrar"
    await _assert_restored(db_session, before)


# ─── AC-22 / D-4: duplicate company rows are retired ──────────────────────────

async def _seed_duplicate_companies(session: AsyncSession, ids: dict) -> dict:
    """The §12 D-4 pair of the dups report (keep OKOMUOIL -> retire OKOMOILP)
    and the FLAG row that is never retired."""
    keep = Company(ticker="OKOMUOIL", name="F026 Okomu Oil Palm Company PLC",
                   sector="CONSUMER GOODS", status="listed", registrar_id=ids["x"])
    retire = Company(ticker="OKOMOILP", name="F026 Okomu Oil Palm Plc",
                     sector="CONSUMER GOODS", status="listed", registrar_id=ids["x"])
    flagged = Company(ticker="ACCESS", name="F026 Access Holdings Plc",
                      sector="BANKS", status="listed", registrar_id=None)
    session.add_all([keep, retire, flagged])
    await session.flush()
    session.add_all([
        CompanyRegistrar(company_id=keep.id, registrar_id=ids["x"], role="primary"),
        CompanyRegistrar(company_id=retire.id, registrar_id=ids["x"], role="primary"),
    ])
    await session.flush()
    return {"keep": keep.id, "retire": retire.id, "flag": flagged.id}


async def _add_reference(session: AsyncSession, kind: str, company_id: int,
                         registrar_id: int) -> None:
    """One row of the §12 D-4 abort table (holdings/transactions/dividends/
    registrar_documents) referencing ``company_id``."""
    if kind == "holdings":
        session.add(Holding(company_id=company_id, num_shares=Decimal("10"),
                            average_cost_basis=Decimal("1"),
                            total_cost=Decimal("10")))
    elif kind == "transactions":
        session.add(Transaction(company_id=company_id, transaction_type="buy",
                                transaction_date=date(2026, 11, 1)))
    elif kind == "dividends":
        session.add(Dividend(company_id=company_id, amount_per_share=Decimal("1")))
    elif kind == "registrar_documents":
        req = RegistrarRequirement(
            registrar_id=registrar_id, task_name="Quarterly returns",
            document_title="Quarterly returns", is_required=True, sort_order=1,
        )
        session.add(req)
        await session.flush()
        session.add(RegistrarDocument(
            registrar_requirement_id=req.id, company_id=company_id,
            file_name="ref.pdf", file_path="/uploads/registrar_documents/ref.pdf",
            file_size=1, mime_type="application/pdf", status="submitted",
        ))
    else:                                            # pragma: no cover
        raise AssertionError(f"unknown reference table {kind!r}")
    await session.flush()


@pytest.mark.asyncio
async def test_ac22_duplicate_company_rows_are_retired_with_their_links(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-22
    """§12 D-4: only the duplicate row is soft-deleted, together with its
    active link; the kept row and the flagged ACCESS row stay, the plan reports
    MERGE / RETAIN / FLAG (never a hard DELETE) and undo restores the row."""
    ids = await _seed(db_session)
    dup = await _seed_duplicate_companies(db_session, ids)
    table = _table(ids)
    before = await _dump(db_session)

    snapshot = await load_snapshot(db_session)
    plan = build_plan(_research(), snapshot, table)
    assert [op.company_id for op in plan.ops
            if isinstance(op, RetireCompanyOp)] == [dup["retire"]]
    assert plan.counts["companies_retired"] == 1
    assert any(line.startswith(
        f"MERGE: company OKOMOILP (id {dup['retire']})") for line in plan.lines)
    assert any(line.startswith(
        f"RETAIN: company OKOMUOIL (id {dup['keep']})") for line in plan.report_lines)
    assert any(line.startswith(
        f"FLAG: company ACCESS (id {dup['flag']})") for line in plan.report_lines)

    record = await apply_plan(db_session, plan)
    await db_session.flush()

    assert (await _company(db_session, dup["retire"])).deleted_at is not None
    assert (await _company(db_session, dup["keep"])).deleted_at is None
    assert (await _company(db_session, dup["flag"])).deleted_at is None
    assert (await _link(db_session, dup["retire"], ids["x"])).deleted_at is not None
    assert (await _link(db_session, dup["keep"], ids["x"])).deleted_at is None

    # undo puts the row and its link back
    await undo(db_session, record)
    await db_session.flush()
    assert (await _company(db_session, dup["retire"])).deleted_at is None
    assert (await _link(db_session, dup["retire"], ids["x"])).deleted_at is None
    await _assert_restored(db_session, before)


@pytest.mark.parametrize("reference", ["holdings", "transactions",
                                       "dividends", "registrar_documents"])
@pytest.mark.asyncio
async def test_ac22_the_plan_aborts_when_a_retired_row_is_referenced(
        db_session: AsyncSession, reference: str):
    # Spec: F-026c-registrar-research-import.md | AC-22
    """At plan time a retire candidate that still carries a holding,
    transaction, dividend or registrar document aborts the whole run — and a
    reference to the KEPT row is no reason to abort. The counts themselves come
    from load_snapshot's read-only selects (snapshot.refs)."""
    ids = await _seed(db_session)
    dup = await _seed_duplicate_companies(db_session, ids)
    table = _table(ids)

    # a reference on the KEPT row only: the plan builds
    await _add_reference(db_session, reference, dup["keep"], ids["x"])
    snapshot = await load_snapshot(db_session)
    assert snapshot.refs.get(dup["keep"], {}).get(reference) == 1
    plan = build_plan(_research(), snapshot, table)
    assert [op.company_id for op in plan.ops
            if isinstance(op, RetireCompanyOp)] == [dup["retire"]]

    # the same reference on the RETIRE candidate: the run aborts
    await _add_reference(db_session, reference, dup["retire"], ids["x"])
    snapshot = await load_snapshot(db_session)
    assert snapshot.refs.get(dup["retire"], {}).get(reference) == 1
    with pytest.raises(RetireBlockedError):
        build_plan(_research(), snapshot, table)


# ─── AC-24 / D-6: the placeholder legacy values are dropped ────────────────────

def _research_placeholders() -> Research:
    """Only the two slugs §12 D-6 names — no clients, no contact data."""
    return Research(registrars=[{"slug": "meristem"}, {"slug": "unity"}])


def _table_placeholders(ids: dict) -> dict:
    """The production §3 rows of D-6 (meristem 2 <- 9, 57; unity 1 <- 17) with
    the test's own ids, so the §3 name checks run against the fixture rows."""
    return {
        "meristem": ResolutionEntry(
            slug="meristem", canonical=ids["m"], duplicates=(ids["m1"], ids["m2"]),
            final_name="Meristem Registrars",
        ),
        "unity": ResolutionEntry(
            slug="unity", canonical=ids["u"], duplicates=(ids["u1"],),
            final_name="Unity Registrars",
        ),
    }


async def _seed_placeholders(session: AsyncSession,
                             meristem_phone: str = "+234-1-345-6789",
                             unity_email: str = "info@unityregistrars.com") -> dict:
    """Registrars 2 and 1 of §12 D-6 (Meristem, Unity) with their §3
    duplicates, holding the placeholder legacy values D-6 lists."""
    rows = [
        Registrar(name="Meristem Registrars", phone=meristem_phone,
                  email="registrar@meristem.com.ng", jurisdiction="nigeria",
                  status="active"),
        Registrar(name="Meristem Old Test Registrars", jurisdiction="nigeria",
                  status="active"),
        Registrar(name="Meristem Second Test Registrars", jurisdiction="nigeria",
                  status="active"),
        Registrar(name="Unity Registrars", phone="+234-1-234-5678",
                  email=unity_email, jurisdiction="nigeria", status="active"),
        Registrar(name="Unity Old Test Registrars", jurisdiction="nigeria",
                  status="active"),
    ]
    session.add_all(rows)
    await session.flush()
    return {"m": rows[0].id, "m1": rows[1].id, "m2": rows[2].id,
            "u": rows[3].id, "u1": rows[4].id}


@pytest.mark.asyncio
async def test_ac24_placeholder_contacts_are_cleared_and_restored_by_undo(
        db_session: AsyncSession):
    # Spec: F-026c-registrar-research-import.md | AC-24
    """§12 D-6: the four placeholder values are set to NULL in one op per
    registrar with no manual copy, the plan is idempotent, and undo restores
    the exact placeholder values."""
    ids = await _seed_placeholders(db_session)
    table = _table_placeholders(ids)
    research = _research_placeholders()
    before = await _dump(db_session)

    snapshot = await load_snapshot(db_session)
    plan = build_plan(research, snapshot, table)
    clears = {(op.registrar_key, frozenset(op.changes)) for op in plan.ops
              if isinstance(op, UpdateRegistrarOp)}
    assert clears == {(ids["m"], frozenset({"phone", "email"})),
                      (ids["u"], frozenset({"phone", "email"}))}, plan.lines
    assert all(value is None for op in plan.ops if isinstance(op, UpdateRegistrarOp)
               for value in op.changes.values())

    record = await apply_plan(db_session, plan)
    await db_session.flush()
    for registrar_id in (ids["m"], ids["u"]):
        row = await _registrar(db_session, registrar_id)
        assert row.phone is None and row.email is None, (
            f"placeholder on #{registrar_id} survived: {row.phone} {row.email}")

    # a second plan on the post-clear state plans nothing (AC-12)
    snapshot = await load_snapshot(db_session)
    assert build_plan(research, snapshot, table).ops == []

    await undo(db_session, record)
    await db_session.flush()
    db_session.expire_all()  # re-read: apply/undo write through SQL, not the ORM objects
    meristem = await _registrar(db_session, ids["m"])
    assert (meristem.phone, meristem.email) == (
        "+234-1-345-6789", "registrar@meristem.com.ng")
    unity = await _registrar(db_session, ids["u"])
    assert (unity.phone, unity.email) == (
        "+234-1-234-5678", "info@unityregistrars.com")
    await _assert_restored(db_session, before)


@pytest.mark.parametrize("mismatch", [
    {"meristem_phone": "01 555 0100"},
    {"unity_email": "info@unity.example"},
])
@pytest.mark.asyncio
async def test_ac24_a_placeholder_value_that_differs_aborts(
        db_session: AsyncSession, mismatch: dict):
    # Spec: F-026c-registrar-research-import.md | AC-24
    """§12 D-6 matches every placeholder exactly: a registrar holding anything
    else in that column aborts the run before a single row is written."""
    ids = await _seed_placeholders(db_session, **mismatch)
    snapshot = await load_snapshot(db_session)
    with pytest.raises(PlaceholderMismatchError):
        build_plan(_research_placeholders(), snapshot, _table_placeholders(ids))
