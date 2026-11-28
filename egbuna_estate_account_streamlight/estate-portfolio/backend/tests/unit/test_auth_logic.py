# backend/tests/unit/test_auth_logic.py
"""
Auth logic unit tests against the current flat architecture.

Targets app.deps (JWT create/decode + FastAPI guards) and the passlib
CryptContext used by the auth router for password hashing. No database —
all session access is mocked.

NOTE: rewritten from the legacy "Stage 1A" version, which imported
app.auth.logic / app.auth.dependencies (modules that never existed in
this repo's tracked history). The real equivalents live in app.deps and
app.routers.auth.pwd_context.
"""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.deps import (
    create_access_token,
    decode_token,
    get_current_user,
    require_admin,
)
from app.routers.auth import pwd_context

SECRET = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM


# ===========================================================================
# Password Hashing (passlib CryptContext used by app.routers.auth)
# ===========================================================================

class TestPasswordHashing:
    def test_password_hashing_produces_bcrypt_hash(self):
        hashed = pwd_context.hash("securepassword123")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_password_hashing_produces_different_hash_each_time(self):
        """bcrypt salts must differ between calls."""
        h1 = pwd_context.hash("same_password")
        h2 = pwd_context.hash("same_password")
        assert h1 != h2

    def test_password_verification_correct_password_returns_true(self):
        hashed = pwd_context.hash("mypassword")
        assert pwd_context.verify("mypassword", hashed) is True

    def test_password_verification_wrong_password_returns_false(self):
        hashed = pwd_context.hash("mypassword")
        assert pwd_context.verify("wrongpassword", hashed) is False

    def test_password_verification_empty_password_returns_false(self):
        hashed = pwd_context.hash("mypassword")
        assert pwd_context.verify("", hashed) is False

    def test_hashed_password_is_not_plaintext(self):
        plaintext = "supersecret"
        hashed = pwd_context.hash(plaintext)
        assert plaintext not in hashed


# ===========================================================================
# JWT Token Creation and Decoding (app.deps)
# ===========================================================================

class TestJWTTokens:
    def test_jwt_token_creation_contains_correct_claims(self):
        token = create_access_token(user_id=1, role="admin")
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["role"] == "admin"

    def test_jwt_token_creation_sets_expiry(self):
        token = create_access_token(user_id=1, role="admin")
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        assert "exp" in payload
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        # Expiry must be in the future by roughly JWT_EXPIRE_DAYS
        assert exp > now

    def test_jwt_token_decode_valid_token_returns_payload(self):
        token = create_access_token(user_id=42, role="readonly")
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "readonly"

    def test_jwt_token_decode_expired_token_raises_401(self):
        token = jwt.encode(
            {"sub": "1", "role": "admin", "exp": int(datetime.now(timezone.utc).timestamp()) - 3600},
            SECRET,
            algorithm=ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401

    def test_jwt_token_decode_tampered_token_raises_401(self):
        token = create_access_token(user_id=1, role="admin")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_token(tampered)
        assert exc_info.value.status_code == 401

    def test_jwt_token_decode_wrong_secret_raises_401(self):
        token = jwt.encode(
            {"sub": "1", "role": "admin", "exp": int(datetime.now(timezone.utc).timestamp()) + 3600},
            "wrong_secret",
            algorithm=ALGORITHM,
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        assert exc_info.value.status_code == 401


# ===========================================================================
# FastAPI Dependencies (app.deps)
# ===========================================================================

class FakeResult:
    def __init__(self, user):
        self._user = user

    def scalar_one_or_none(self):
        return self._user


class FakeSession:
    def __init__(self, user):
        self._user = user

    async def execute(self, *_args, **_kwargs):
        return FakeResult(self._user)


class TestFastAPIDependencies:
    @pytest.mark.asyncio
    async def test_require_admin_dependency_admin_role_passes(self):
        mock_user = MagicMock()
        mock_user.role = "admin"
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
    async def test_get_current_user_valid_cookie_returns_user(self):
        token = create_access_token(user_id=1, role="admin")
        user = SimpleNamespace(id=1, username="zubbyik", role="admin", is_active=True, deleted_at=None)
        result = await get_current_user(epm_token=token, session=FakeSession(user))
        assert result.username == "zubbyik"

    @pytest.mark.asyncio
    async def test_get_current_user_missing_cookie_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(epm_token=None, session=FakeSession(None))
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user_in_db_raises_401(self):
        token = create_access_token(user_id=999, role="admin")
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(epm_token=token, session=FakeSession(None))
        assert exc_info.value.status_code == 401