# backend/tests/unit/test_auth_logic.py
"""
Stage 1A.1 — Authentication Logic Unit Tests
No database. All dependencies mocked.
Tests password hashing, JWT creation/decoding, and FastAPI dependency guards.
"""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

# ---------------------------------------------------------------------------
# Adjust these imports to match your actual module paths
# ---------------------------------------------------------------------------
from app.auth.logic import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.auth.dependencies import get_current_user, require_admin
from app.config import settings

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SECRET = settings.jwt_secret
ALGORITHM = "HS256"
ADMIN_USER = {"id": 1, "username": "zubbyik", "name": "Zubby", "role": "admin"}
READONLY_USER = {"id": 2, "username": "viewer", "name": "Viewer", "role": "readonly"}


# ===========================================================================
# 1A.1 — Password Hashing
# ===========================================================================

class TestPasswordHashing:
    def test_password_hashing_produces_bcrypt_hash(self):
        hashed = hash_password("securepassword123")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_password_hashing_produces_different_hash_each_time(self):
        """bcrypt salts must differ between calls."""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2

    def test_password_verification_correct_password_returns_true(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_password_verification_wrong_password_returns_false(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_password_verification_empty_password_returns_false(self):
        hashed = hash_password("mypassword")
        assert verify_password("", hashed) is False

    def test_hashed_password_is_not_plaintext(self):
        plaintext = "supersecret"
        hashed = hash_password(plaintext)
        assert plaintext not in hashed


# ===========================================================================
# 1A.1 — JWT Token Creation and Decoding
# ===========================================================================

class TestJWTTokens:
    def test_jwt_token_creation_contains_correct_claims(self):
        token = create_access_token(data={"sub": "zubbyik", "role": "admin"})
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        assert payload["sub"] == "zubbyik"
        assert payload["role"] == "admin"

    def test_jwt_token_creation_sets_correct_expiry(self):
        token = create_access_token(
            data={"sub": "zubbyik", "role": "admin"},
            expires_delta=timedelta(days=30),
        )
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        # Should expire ~30 days from now (within 60-second tolerance)
        assert timedelta(days=29, hours=23) < (exp - now) < timedelta(days=30, minutes=1)

    def test_jwt_token_decode_valid_token_returns_payload(self):
        token = create_access_token(data={"sub": "zubbyik", "role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == "zubbyik"
        assert payload["role"] == "admin"

    def test_jwt_token_decode_expired_token_raises_exception(self):
        token = create_access_token(
            data={"sub": "zubbyik", "role": "admin"},
            expires_delta=timedelta(seconds=-1),  # already expired
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_jwt_token_decode_tampered_token_raises_exception(self):
        token = create_access_token(data={"sub": "zubbyik", "role": "admin"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401

    def test_jwt_token_decode_wrong_secret_raises_exception(self):
        token = jwt.encode(
            {"sub": "zubbyik", "role": "admin", "exp": time.time() + 3600},
            "wrong_secret",
            algorithm=ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401


# ===========================================================================
# 1A.1 — FastAPI Dependencies
# ===========================================================================

class TestFastAPIDependencies:
    @pytest.mark.asyncio
    async def test_require_admin_dependency_admin_role_passes(self):
        """Admin user passes require_admin without raising."""
        mock_user = MagicMock()
        mock_user.role = "admin"
        # Should return user without raising
        result = await require_admin(current_user=mock_user)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_admin_dependency_readonly_role_raises_403(self):
        mock_user = MagicMock()
        mock_user.role = "readonly"
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=mock_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_admin_dependency_no_user_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=None)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_valid_cookie_returns_user(self):
        token = create_access_token(data={"sub": "zubbyik", "role": "admin"})
        mock_db = AsyncMock()
        mock_db_user = MagicMock()
        mock_db_user.id = 1
        mock_db_user.username = "zubbyik"
        mock_db_user.role = "admin"
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_db_user

        with patch("app.auth.dependencies.get_db", return_value=mock_db):
            user = await get_current_user(epm_token=token, db=mock_db)
        assert user.username == "zubbyik"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_cookie_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(epm_token=None, db=AsyncMock())
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user_in_db_raises_401(self):
        token = create_access_token(data={"sub": "ghost_user", "role": "admin"})
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(epm_token=token, db=mock_db)
        assert exc_info.value.status_code == 401
