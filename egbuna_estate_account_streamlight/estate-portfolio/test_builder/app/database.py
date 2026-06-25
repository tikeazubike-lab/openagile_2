import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def _build_engine_url():
    return os.environ.get("DATABASE_URL", "sqlite+aiosqlite:////data/test_builder.db")


engine = None
SessionLocal = None


def _ensure_engine():
    global engine, SessionLocal
    if engine is None:
        engine = create_async_engine(_build_engine_url(), echo=False)
        SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create tables on startup, enable WAL mode, seed default domain codes."""
    _ensure_engine()
    # Import models so they register with Base.metadata before create_all
    from app import models  # noqa: F401
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrent read/write
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)

        # Seed default domain codes if table is empty
        from app.seed import DEFAULT_DOMAIN_CODES
        result = await conn.execute(text("SELECT COUNT(*) FROM domain_codes"))
        count = result.scalar()
        if count == 0:
            for code, label, folder_slug in DEFAULT_DOMAIN_CODES:
                await conn.execute(
                    text(
                        "INSERT INTO domain_codes (code, label, folder_slug) VALUES (:code, :label, :folder_slug)"
                    ),
                    {"code": code, "label": label, "folder_slug": folder_slug},
                )


async def get_session():
    _ensure_engine()
    async with SessionLocal() as session:
        yield session
