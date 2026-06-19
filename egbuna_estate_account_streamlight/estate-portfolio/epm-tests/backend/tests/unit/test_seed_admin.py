# backend/tests/unit/test_seed_admin.py
"""
Stage 1A.5 — seed_admin.py Unit Tests
Verifies admin seeding is idempotent, reads from env, and hashes correctly.
All DB calls are mocked — no real database needed.
"""
import os
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

# Adjust import path to match your actual seed script location
from app.scripts.seed_admin import seed_admin_user


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "zubbyik")
    monkeypatch.setenv("ADMIN_PASSWORD", "TestPassword123!")


def make_mock_session(existing_user=None):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_user
    session.execute.return_value = result
    return session


# ===========================================================================
# 1A.5 — Tests
# ===========================================================================

class TestSeedAdminUser:
    @pytest.mark.asyncio
    async def test_seed_admin_creates_user_when_none_exists(self):
        """When no admin exists, a new user row must be inserted."""
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        session.add.assert_called_once()
        session.commit.assert_called_once()
        created_user = session.add.call_args[0][0]
        assert created_user.username == "zubbyik"

    @pytest.mark.asyncio
    async def test_seed_admin_is_idempotent_when_user_already_exists(self):
        """Re-running seed must NOT insert a second user or crash."""
        existing = MagicMock()
        existing.username = "zubbyik"
        session = make_mock_session(existing_user=existing)

        await seed_admin_user(session)

        session.add.assert_not_called()
        session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_seed_admin_reads_password_from_environment_variable(self, monkeypatch):
        monkeypatch.setenv("ADMIN_PASSWORD", "EnvProvidedPass!")
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        # The password_hash must be derived from the env var value
        from app.auth.logic import verify_password
        assert verify_password("EnvProvidedPass!", created_user.password_hash)

    @pytest.mark.asyncio
    async def test_seed_admin_does_not_use_hardcoded_credentials(self, monkeypatch):
        """Ensure script crashes (KeyError) if env var is absent, not falls back to hardcode."""
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

        session = make_mock_session(existing_user=None)
        with pytest.raises((KeyError, SystemExit, ValueError)):
            await seed_admin_user(session)

    @pytest.mark.asyncio
    async def test_seed_admin_hashed_password_is_not_plaintext_in_db(self):
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        # Hash must start with bcrypt prefix
        assert created_user.password_hash.startswith("$2b$") or \
               created_user.password_hash.startswith("$2a$")
        # Plaintext must NOT be stored
        assert created_user.password_hash != "TestPassword123!"

    @pytest.mark.asyncio
    async def test_seed_admin_sets_role_to_admin(self):
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        assert created_user.role == "admin"

    @pytest.mark.asyncio
    async def test_seed_admin_sets_is_active_true(self):
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        assert created_user.is_active is True