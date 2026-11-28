# backend/tests/unit/test_seed_admin.py
"""
Unit tests for scripts/seed_admin.py (seed_admin_user function).

Verifies admin seeding is idempotent, reads from env, and hashes correctly.
All DB calls are mocked — no real database needed.

NOTE: rewritten from the legacy "Stage 1A" version, which imported
app.scripts.seed_admin (a module that never existed — the script lives at
scripts/seed_admin.py). The script now exposes a session-injectable
seed_admin_user() function so its logic is actually testable.
"""
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.seed_admin import seed_admin_user, pwd_context


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("EPM_ADMIN_USERNAME", "zubbyik")
    monkeypatch.setenv("EPM_ADMIN_PASSWORD", "TestPassword123!")


def make_mock_session(existing_user=None):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_user
    session.execute.return_value = result
    return session


class TestSeedAdminUser:
    @pytest.mark.asyncio
    async def test_seed_admin_creates_user_when_none_exists(self):
        """When no admin exists, a new user row must be inserted."""
        session = make_mock_session(existing_user=None)

        result = await seed_admin_user(session)

        assert result["created"] is True
        assert result["updated"] is False
        session.add.assert_called_once()
        session.commit.assert_called_once()
        created_user = session.add.call_args[0][0]
        assert created_user.username == "zubbyik"

    @pytest.mark.asyncio
    async def test_seed_admin_is_idempotent_when_user_already_exists(self):
        """Re-running seed must update the password, not insert a second user."""
        existing = MagicMock()
        existing.username = "zubbyik"
        session = make_mock_session(existing_user=existing)

        result = await seed_admin_user(session)

        assert result["created"] is False
        assert result["updated"] is True
        # Existing row is re-added (to persist the password update), not a new user
        assert session.add.call_args[0][0] is existing
        session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_admin_reads_password_from_environment_variable(self, monkeypatch):
        monkeypatch.setenv("EPM_ADMIN_PASSWORD", "EnvProvidedPass!")
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        assert pwd_context.verify("EnvProvidedPass!", created_user.hashed_password)

    @pytest.mark.asyncio
    async def test_seed_admin_does_not_use_hardcoded_credentials(self, monkeypatch):
        """Missing env var must raise, not fall back to a hardcoded password."""
        monkeypatch.delenv("EPM_ADMIN_PASSWORD", raising=False)

        session = make_mock_session(existing_user=None)
        with pytest.raises(ValueError, match="EPM_ADMIN_PASSWORD"):
            await seed_admin_user(session)

    @pytest.mark.asyncio
    async def test_seed_admin_hashed_password_is_not_plaintext_in_db(self):
        session = make_mock_session(existing_user=None)

        await seed_admin_user(session)

        created_user = session.add.call_args[0][0]
        assert created_user.hashed_password.startswith("$2b$") or created_user.hashed_password.startswith("$2a$")
        assert created_user.hashed_password != "TestPassword123!"

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