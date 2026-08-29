"""
F-026b — Tests for seed script idempotency and entity handling.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    Company, Registrar, CompanyRegistrar,
)


@pytest.mark.asyncio
async def test_seed_idempotency(db_session: AsyncSession):
    """Running seed twice produces zero new rows on second run."""
    from scripts.seed_registrar_mapping import (
        seed_registrars, seed_companies, seed_links, seed_special_links,
    )

    r1 = await seed_registrars(db_session)
    c1 = await seed_companies(db_session)
    l1 = await seed_links(db_session)
    s1 = await seed_special_links(db_session)

    first_created = r1["created"] + c1["created"] + l1["created"] + s1["created"]
    assert first_created > 0, "First run should create rows"

    r2 = await seed_registrars(db_session)
    c2 = await seed_companies(db_session)
    l2 = await seed_links(db_session)
    s2 = await seed_special_links(db_session)

    second_created = r2["created"] + c2["created"] + l2["created"] + s2["created"]
    assert second_created == 0, f"Second run created {second_created} rows"


@pytest.mark.asyncio
async def test_seplat_coregistration(db_session: AsyncSession):
    """Seplat has DataMax (primary) + Computershare UK (co_registrar)."""
    from scripts.seed_registrar_mapping import (
        seed_registrars, seed_companies, seed_links, seed_special_links,
    )
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
async def test_africa_prudential_dual_entity(db_session: AsyncSession):
    """Africa Prudential Plc exists as both company and registrar, independently."""
    from scripts.seed_registrar_mapping import (
        seed_registrars, seed_companies, seed_links, seed_special_links,
    )
    await seed_registrars(db_session)
    await seed_companies(db_session)
    await seed_links(db_session)
    await seed_special_links(db_session)

    # Find as company
    result = await db_session.execute(
        select(Company).where(Company.ticker == "AFPRUD")
    )
    company = result.scalar_one_or_none()
    assert company is not None
    assert company.name == "Africa Prudential Plc"

    # Find as registrar
    result = await db_session.execute(
        select(Registrar).where(Registrar.name == "Africa Prudential Registrars Limited")
    )
    registrar = result.scalar_one_or_none()
    assert registrar is not None

    # Different records
    assert company.id != registrar.id

    # Self-registration link
    result = await db_session.execute(
        select(CompanyRegistrar).where(
            CompanyRegistrar.company_id == company.id,
            CompanyRegistrar.registrar_id == registrar.id,
        )
    )
    link = result.scalar_one_or_none()
    assert link is not None
    assert link.role == "primary"


@pytest.mark.asyncio
async def test_seed_company_count(db_session: AsyncSession):
    """
    Dynamic company-count relative invariant: the number of companies seeded
    by seed_companies equals the number of distinct tickers declared in the
    seed data (COMPANY_GROUPS + UNMAPPED_COMPANIES). A relative invariant,
    not a hardcoded count — recomputed from the data itself.
    """
    from scripts.seed_registrar_mapping import (
        seed_companies, COMPANY_GROUPS, UNMAPPED_COMPANIES,
    )

    expected_tickers = set()
    for _registrar_name, companies in COMPANY_GROUPS:
        for _name, ticker, _sec_type in companies:
            if ticker:
                expected_tickers.add(ticker)
    for spec in UNMAPPED_COMPANIES:
        if spec.ticker:
            expected_tickers.add(spec.ticker)

    result = await seed_companies(db_session)
    total = result["created"] + result["existing"]

    assert total == len(expected_tickers), (
        f"Seed produced {total} companies, expected {len(expected_tickers)} "
        f"(distinct tickers in seed data)"
    )
