# backend/tests/integration/conftest.py
"""
Shared fixtures for ALL integration, contract, and database tests.

KEY DESIGN — Zero side-effects on shared openagile_postgres:
  Every test that touches the database runs inside a SAVEPOINT transaction.
  The outer transaction is never committed. A ROLLBACK at teardown restores
  the database to its exact pre-test state, regardless of what the test did.

Connection:
  Uses openagile_network DNS (container name openagile_postgres) via env vars.
  Secrets injected by GitHub Actions (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD).

Never run this against production data without the rollback fixture.
"""
import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base, get_db
from app.auth.logic import create_access_token, hash_password
from app.models.users import User

# ---------------------------------------------------------------------------
# Build DSN from GitHub Actions secrets / environment
# ---------------------------------------------------------------------------

DB_HOST = os.environ["DB_HOST"]          # e.g. openagile_postgres
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ["DB_NAME"]          # e.g. estate_portfolio
DB_USER = os.environ["DB_USER"]          # e.g. openagile
DB_PASSWORD = os.environ["DB_PASSWORD"]

DB_TEST_SCHEMA = os.environ.get("DB_TEST_SCHEMA", "estate_portfolio_test")

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?options=-csearch_path%3D{DB_TEST_SCHEMA}"
)

# NullPool: never reuse connections between tests (clean slate every time)
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)


# ---------------------------------------------------------------------------
# Event loop (module-scoped for async fixtures)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Core rollback fixture
# Each test gets a fresh connection, starts a transaction, yields a session,
# then rolls back — the DB is exactly as it was before the test ran.
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as conn:
        # Begin outer transaction — this will NEVER be committed
        await conn.begin()
        # Create a savepoint so individual test failures don't abort the outer tx
        await conn.begin_nested()

        session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            # Roll back ALL changes made during this test
            await conn.rollback()


# ---------------------------------------------------------------------------
# FastAPI app with DB overridden to use the rollback session
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_app(db_session: AsyncSession):
    """FastAPI app wired to the rollback DB session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# HTTP clients (authenticated + anonymous)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    token = create_access_token(data={"sub": "test_admin", "role": "admin"})
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        cookies={"epm_token": token},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def user_http_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    token = create_access_token(data={"sub": "test_viewer", "role": "readonly"})
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        cookies={"epm_token": token},
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Seed fixtures — insert test data that lives only for the current test
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    user = User(
        username="test_admin",
        name="Test Admin",
        password_hash=hash_password("testpass123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()  # get user.id without committing
    return user


@pytest_asyncio.fixture
async def test_readonly_user(db_session: AsyncSession) -> User:
    user = User(
        username="test_viewer",
        name="Test Viewer",
        password_hash=hash_password("viewpass123"),
        role="readonly",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_company(db_session: AsyncSession):
    from app.models.companies import Company
    company = Company(
        ticker="TESTCO",
        name="Test Company Ltd",
        sector="Banking",
        status="active",
    )
    db_session.add(company)
    await db_session.flush()
    return company


@pytest_asyncio.fixture
async def test_live_holding(db_session: AsyncSession, test_company):
    from app.models.holdings import Holding
    holding = Holding(
        company_id=test_company.id,
        num_shares=100,
        avg_purchase_price="450.00",
        status="live",
    )
    db_session.add(holding)
    await db_session.flush()
    return holding


@pytest_asyncio.fixture
async def test_draft_holding(db_session: AsyncSession, test_company):
    from app.models.holdings import Holding
    # Use a different company to avoid UNIQUE constraint collision with test_live_holding
    from app.models.companies import Company
    company2 = Company(
        ticker="DRAFTCO",
        name="Draft Company Ltd",
        sector="Consumer Goods",
        status="active",
    )
    db_session.add(company2)
    await db_session.flush()

    holding = Holding(
        company_id=company2.id,
        num_shares=50,
        avg_purchase_price="200.00",
        status="draft",
    )
    db_session.add(holding)
    await db_session.flush()
    return holding