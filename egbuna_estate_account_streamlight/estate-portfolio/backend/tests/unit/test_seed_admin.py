# backend/tests/unit/test_seed_admin.py
"""
Tests for scripts/seed_admin.py — seed() function.
The real script always overwrites the admin password on re-run (by design,
for GitHub Secret rotation). Tests verify this intentional behavior.
"""
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import AsyncSessionLocal
from app.models import User


def _import_seed_and_patch():
    """
    Import seed() from scripts/seed_admin.py and return it along with a
    patcher for its AsyncSessionLocal reference.
    """
    import sys
    from pathlib import Path
    backend_root = Path(__file__).resolve().parents[2]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    import scripts.seed_admin
    return scripts.seed_admin.seed, scripts.seed_admin


# ===========================================================================
# Tests
# ===========================================================================

class TestSeedAdmin:
    def _run_seed(self, mock_db, env_vars=None):
        """Helper: import seed, patch its dependencies, and run it."""
        seed, mod = _import_seed_and_patch()
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_db)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        class MockMaker:
            def __call__(self):
                return mock_cm

        env = env_vars or {
            "EPM_ADMIN_USERNAME": "zubbyik",
            "EPM_ADMIN_NAME": "Zubby",
            "EPM_ADMIN_PASSWORD": "testpass123",
        }

        with patch.object(mod, "AsyncSessionLocal", MockMaker()):
            with patch.dict(os.environ, env, clear=True):
                return asyncio.run(seed())

    def test_seed_creates_user_when_none_exists(self):
        """No existing user → seed() creates a new admin user."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        self._run_seed(mock_db)

        assert mock_db.add.called
        added_user = mock_db.add.call_args[0][0]
        assert added_user.username == "zubbyik"
        assert added_user.role == "admin"
        assert added_user.is_active is True
        assert added_user.hashed_password.startswith("$2b$")

    def test_seed_overwrites_password_when_user_exists(self):
        """Existing user → seed() overwrites password (confirmed intentional)."""
        existing_user = MagicMock(spec=User)
        existing_user.username = "zubbyik"
        existing_user.name = "Zubby"
        existing_user.hashed_password = "old_hash"
        existing_user.role = "admin"
        existing_user.is_active = True

        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=existing_user))
        mock_db.commit = AsyncMock()

        self._run_seed(mock_db)

        assert existing_user.hashed_password.startswith("$2b$")
        assert existing_user.hashed_password != "old_hash"

    def test_seed_requires_password_env_var(self):
        """Missing EPM_ADMIN_PASSWORD → seed() exits with error."""
        mock_db = MagicMock()
        with pytest.raises(SystemExit):
            self._run_seed(mock_db, env_vars={
                "EPM_ADMIN_USERNAME": "zubbyik",
                "EPM_ADMIN_NAME": "Zubby",
            })

    def test_seed_hashed_password_is_not_plaintext(self):
        """Password hash must differ from plaintext password."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        plaintext = "supersecret"
        self._run_seed(mock_db, env_vars={
            "EPM_ADMIN_USERNAME": "zubbyik",
            "EPM_ADMIN_NAME": "Zubby",
            "EPM_ADMIN_PASSWORD": plaintext,
        })

        added_user = mock_db.add.call_args[0][0]
        assert added_user.hashed_password.startswith("$2b$")
        assert plaintext not in added_user.hashed_password

    def test_seed_sets_role_to_admin(self):
        """Created user must have admin role."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        self._run_seed(mock_db)

        added_user = mock_db.add.call_args[0][0]
        assert added_user.role == "admin"

    def test_seed_sets_is_active_true(self):
        """Created user must be active."""
        mock_db = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        self._run_seed(mock_db)

        added_user = mock_db.add.call_args[0][0]
        assert added_user.is_active is True
