"""
EPM — Async database engine and session factory.
Uses SQLAlchemy 2.0 async API with asyncpg driver.
The engine + session are created once at import time.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ── Engine ─────────────────────────────────────────────────────────────────────
# pool_pre_ping=True checks the connection before handing it out from the pool,
# handling the case where the shared Postgres container restarts.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.is_dev,  # SQL logging in dev only
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── ORM Base ───────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass
