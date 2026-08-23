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
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.database import Base
from app.deps import create_access_token, get_session
from app.models import User


def _unique_suffix() -> str:
    """Short unique suffix for test usernames so residual DB rows never collide."""
    import time
    return f"{int(time.time() * 1000)}"

# ---------------------------------------------------------------------------
# Build DSN from GitHub Actions secrets / environment
# ---------------------------------------------------------------------------

DB_HOST = os.environ["DB_HOST"]          # e.g. openagile_postgres
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "epm_test")  # isolated test database
DB_USER = os.environ["DB_USER"]          # e.g. openagile
DB_PASSWORD = os.environ["DB_PASSWORD"]

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# NullPool: never reuse connections between tests (clean slate every time)
engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)


# ── Create tables in the test database ──────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_test_tables():
    """Create test database tables once per session (native pytest-asyncio loop).

    A custom event_loop fixture was previously used; a session-scoped loop
    mismatched function-scoped async fixtures and caused random hangs on the
    users-table connection. With pytest.ini's asyncio_default_*_loop_scope=session,
    everything shares one loop and the asyncpg connections are awaited on the
    loop that created them.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


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

    app.dependency_overrides[get_session] = override_get_db
    yield app
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# HTTP clients (authenticated + anonymous)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def admin_http_client(test_app, db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Authenticated admin client. The admin user is created INSIDE the rollback
    db_session (not via a separate committed connection), so the fixture never
    contends with db_session's uncommitted INSERTs on the users unique index —
    a transactionid deadlock occurred previously when both were active.

    A unique username avoids collisions with rows left behind by older runs.
    """
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"])
    user = User(
        username=f"test_admin_http_{_unique_suffix()}",
        name="Test Admin HTTP",
        hashed_password=pwd.hash("testpass123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user_id=user.id, role="admin")

    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        cookies={"epm_token": token},
    ) as client:
        yield client


@pytest_asyncio.fixture
async def user_http_client(test_app, db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Authenticated readonly client. Same rollback-session pattern as
    admin_http_client to avoid the users-table index deadlock.
    """
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"])
    user = User(
        username=f"test_viewer_http_{_unique_suffix()}",
        name="Test Viewer HTTP",
        hashed_password=pwd.hash("viewpass123"),
        role="readonly",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    token = create_access_token(user_id=user.id, role="readonly")
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        cookies={"epm_token": token},
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Seed fixtures — insert test data that lives only for the current test
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"])
    user = User(
        username="test_admin",
        name="Test Admin",
        hashed_password=pwd.hash("testpass123"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()  # get user.id without committing
    return user


@pytest_asyncio.fixture
async def test_readonly_user(db_session: AsyncSession) -> User:
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"])
    user = User(
        username="test_viewer",
        name="Test Viewer",
        hashed_password=pwd.hash("viewpass123"),
        role="readonly",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_company(db_session: AsyncSession):
    from app.models import Company
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
    from app.models import Holding
    holding = Holding(
        company_id=test_company.id,
        num_shares=100,
        average_cost_basis=450.00,
        total_cost=45000.00,
        holding_type="active",
    )
    db_session.add(holding)
    await db_session.flush()
    return holding


@pytest_asyncio.fixture
async def test_draft_holding(db_session: AsyncSession, test_company):
    from app.models import Holding, Company
    # Use a different company to avoid UNIQUE constraint collision with test_live_holding
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
        average_cost_basis=200.00,
        total_cost=10000.00,
        holding_type="draft",
    )
    db_session.add(holding)
    await db_session.flush()
    return holding