#!/usr/bin/env python3
"""
EPM — Seed admin user.
Idempotent: does nothing if the admin user already exists.

Usage (run inside the epm container after alembic upgrade head):
  python scripts/seed_admin.py

Reads from environment:
  EPM_ADMIN_USERNAME  (default: zubbyik)
  EPM_ADMIN_NAME      (default: Zubby)
  EPM_ADMIN_PASSWORD  (REQUIRED — no default)
"""

import asyncio
import os
import sys

# Add the parent directory (backend/) to sys.path so app.* imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from passlib.context import CryptContext
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed() -> None:
    admin_username = os.environ.get("EPM_ADMIN_USERNAME", "zubbyik")
    admin_name = os.environ.get("EPM_ADMIN_NAME", "Zubby")
    admin_password = os.environ.get("EPM_ADMIN_PASSWORD")

    if not admin_password:
        print("ERROR: EPM_ADMIN_PASSWORD env var is required", file=sys.stderr)
        sys.exit(1)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == admin_username)
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update password for existing user if script runs again (e.g. when GitHub Secret is updated)
            existing.hashed_password = pwd_context.hash(admin_password)
            session.add(existing)
            await session.commit()
            print(f"✅ Admin user '{admin_username}' already exists — password updated.")
            return

        user = User(
            username=admin_username,
            name=admin_name,
            hashed_password=pwd_context.hash(admin_password),
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print(f"✅ Admin user '{admin_username}' created successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
