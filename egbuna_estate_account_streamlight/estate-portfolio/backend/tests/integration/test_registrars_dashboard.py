"""
F-026 — Tests for registrar dashboard and seed script.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from httpx import AsyncClient

from app.models import (
    Company, Registrar, RegistrarRequirement, RegistrarDocument,
    CompanyRegistrar, User,
)


# ─── Dashboard Tests ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def seeded_registrars(db_session: AsyncSession):
    """Seed registrars with known state for testing."""
    reg_complete = Registrar(name="Complete Registrar", jurisdiction="nigeria")
    reg_attention = Registrar(name="Attention Registrar", jurisdiction="nigeria")
    reg_nodata = Registrar(name="No Data Registrar", jurisdiction="nigeria")
    db_session.add_all([reg_complete, reg_attention, reg_nodata])
    await db_session.flush()

    # Complete registrar: 2 requirements, both completed
    req1 = RegistrarRequirement(
        registrar_id=reg_complete.id, task_name="Task A", document_title="Doc A",
        is_required=True, sort_order=0,
    )
    req2 = RegistrarRequirement(
        registrar_id=reg_complete.id, task_name="Task B", document_title="Doc B",
        is_required=True, sort_order=1,
    )
    db_session.add_all([req1, req2])
    await db_session.flush()

    doc1 = RegistrarDocument(
        registrar_requirement_id=req1.id, file_name="a.pdf", file_path="/tmp/a.pdf",
        file_size=100, mime_type="application/pdf", status="completed",
    )
    doc2 = RegistrarDocument(
        registrar_requirement_id=req2.id, file_name="b.pdf", file_path="/tmp/b.pdf",
        file_size=200, mime_type="application/pdf", status="completed",
    )
    db_session.add_all([doc1, doc2])

    # Attention registrar: 1 requirement, pending
    req3 = RegistrarRequirement(
        registrar_id=reg_attention.id, task_name="Task C", document_title="Doc C",
        is_required=True, sort_order=0,
    )
    db_session.add(req3)
    await db_session.flush()

    return {
        "complete": reg_complete,
        "attention": reg_attention,
        "nodata": reg_nodata,
        "req1": req1, "req2": req2, "req3": req3,
    }


@pytest.mark.asyncio
async def test_dashboard_summary_completion_pct(
    admin_http_client: AsyncClient,
    seeded_registrars,
):
    """completion_pct = completed / total * 100."""
    response = await admin_http_client.get("/api/v1/registrars/dashboard-summary")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_requirements"] == 3
    assert data["completed_requirements"] == 2
    assert data["completion_pct"] == 66.7


@pytest.mark.asyncio
async def test_dashboard_summary_registrar_health(
    admin_http_client: AsyncClient,
    seeded_registrars,
):
    """registrar_health categorizes registrars correctly."""
    response = await admin_http_client.get("/api/v1/registrars/dashboard-summary")
    assert response.status_code == 200
    health = response.json()["data"]["registrar_health"]
    assert health["complete"] == 1
    assert health["attention"] == 1
    assert health["no_data"] == 1


@pytest.mark.asyncio
async def test_global_tracker_pagination(
    admin_http_client: AsyncClient,
    seeded_registrars,
):
    """global-tracker returns correct pagination metadata."""
    response = await admin_http_client.get(
        "/api/v1/registrar-requirements/global-tracker?page=1&page_size=2"
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 3
    assert data["total_pages"] == 2
    assert len(data["rows"]) == 2


@pytest.mark.asyncio
async def test_global_tracker_status_field(
    admin_http_client: AsyncClient,
    seeded_registrars,
):
    """global-tracker status field reflects document state."""
    response = await admin_http_client.get(
        "/api/v1/registrar-requirements/global-tracker?page=1&page_size=10"
    )
    rows = response.json()["data"]["rows"]
    statuses = {r["task_name"]: r["status"] for r in rows}
    assert statuses["Task A"] == "completed"
    assert statuses["Task B"] == "completed"
    assert statuses["Task C"] == "pending"


@pytest.mark.asyncio
async def test_company_registrars_backfill(db_session: AsyncSession):
    """Backfill from companies.registrar_id preserves all relationships."""
    from scripts.seed_registrar_mapping import seed_registrars, seed_companies, seed_links, seed_special_links
    await seed_registrars(db_session)
    await seed_companies(db_session)
    await seed_links(db_session)
    await seed_special_links(db_session)

    result = await db_session.execute(
        select(CompanyRegistrar).where(CompanyRegistrar.deleted_at.is_(None))
    )
    links = result.scalars().all()
    assert len(links) > 0


@pytest.mark.asyncio
async def test_company_registrars_unique_constraint(db_session: AsyncSession):
    """Duplicate (company_id, registrar_id) pair is rejected."""
    from sqlalchemy.exc import IntegrityError

    reg = Registrar(name="Unique Test Registrar")
    db_session.add(reg)
    await db_session.flush()

    co = Company(name="Unique Co", ticker="UCT1")
    db_session.add(co)
    await db_session.flush()

    link1 = CompanyRegistrar(company_id=co.id, registrar_id=reg.id, role="primary")
    db_session.add(link1)
    await db_session.flush()

    link2 = CompanyRegistrar(company_id=co.id, registrar_id=reg.id, role="primary")
    db_session.add(link2)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_seplat_coregistration(db_session: AsyncSession):
    """Seplat has DataMax (primary) + Computershare UK (co_registrar)."""
    from scripts.seed_registrar_mapping import seed_registrars, seed_companies, seed_links, seed_special_links
    await seed_registrars(db_session)
    await seed_companies(db_session)
    await seed_links(db_session)
    await seed_special_links(db_session)

    result = await db_session.execute(
        select(Company).where(Company.ticker == "SEPLAT")
    )
    seplat = result.scalar_one_or_none()
    assert seplat is not None

    result = await db_session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == seplat.id,
            CompanyRegistrar.deleted_at.is_(None),
        )
    )
    links = result.scalars().all()
    assert len(links) == 2

    link_map = {}
    for link in links:
        reg = await db_session.get(Registrar, link.registrar_id)
        link_map[reg.name] = link.role

    assert "DataMax Registrars Limited" in link_map
    assert link_map["DataMax Registrars Limited"] == "primary"
    assert "Computershare UK" in link_map
    assert link_map["Computershare UK"] == "co_registrar"


@pytest.mark.asyncio
async def test_seed_idempotency(db_session: AsyncSession):
    """Running seed twice produces zero new rows on second run."""
    from scripts.seed_registrar_mapping import seed_registrars, seed_companies, seed_links, seed_special_links

    r1 = await seed_registrars(db_session)
    c1 = await seed_companies(db_session)
    l1 = await seed_links(db_session)
    s1 = await seed_special_links(db_session)

    first_created = r1["created"] + c1["created"] + l1["created"] + s1["created"]
    assert first_created > 0

    r2 = await seed_registrars(db_session)
    c2 = await seed_companies(db_session)
    l2 = await seed_links(db_session)
    s2 = await seed_special_links(db_session)

    second_created = r2["created"] + c2["created"] + l2["created"] + s2["created"]
    assert second_created == 0, f"Second run created {second_created} rows"
