# backend/tests/unit/test_api_routes.py
"""
API route unit tests against the current flat architecture.

Endpoint functions are called directly with mocked sessions (the modern
pattern used by test_auth_router.py / test_holdings_router.py) rather than
through TestClient + app.main, so no HTTP transport is exercised.

NOTE: rewritten from the legacy "Stage 1A" version, which imported
app.auth.logic and relied on app.routers.*.get_db (neither exists today —
auth helpers live in app.deps and DB sessions come from get_session).
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Response

from app.routers.auth import (
    change_password,
    login,
    logout,
    me,
    ChangePasswordRequest,
    LoginRequest,
)

PASSWORD_HASH = "$2b$12$5JOVNxT0x5j0g8iM4d0PO.FSnC7XXIQK5lLylJ.gUvVf2fd2A4J3K"


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

    async def commit(self):
        pass


def make_user(**overrides):
    fields = dict(
        id=1,
        username="zubbyik",
        name="Zubby",
        role="admin",
        is_active=True,
        deleted_at=None,
        hashed_password=PASSWORD_HASH,
    )
    fields.update(overrides)
    return SimpleNamespace(**fields)


# ===========================================================================
# Auth Endpoints
# ===========================================================================

class TestLoginEndpoint:
    def test_login_valid_credentials_sets_httponly_cookie(self):
        response = Response()
        body = LoginRequest(username="zubbyik", password="testpassword")
        with patch("app.routers.auth.pwd_context.verify", return_value=True), \
             patch("app.routers.auth.create_access_token", return_value="fake.jwt.token"):
            payload = asyncio_run(login(body, response, FakeSession(make_user())))

        assert payload["data"]["username"] == "zubbyik"
        assert payload["data"]["role"] == "admin"
        assert "password_hash" not in payload["data"]
        set_cookie = response.headers.get("set-cookie", "")
        assert "epm_token=fake.jwt.token" in set_cookie
        assert "HttpOnly" in set_cookie

    def test_login_invalid_credentials_raises_401(self):
        response = Response()
        body = LoginRequest(username="zubbyik", password="wrongpassword")
        with patch("app.routers.auth.pwd_context.verify", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                asyncio_run(login(body, response, FakeSession(make_user())))
        assert exc_info.value.status_code == 401

    def test_login_nonexistent_user_raises_401(self):
        response = Response()
        body = LoginRequest(username="ghost", password="anypassword")
        with pytest.raises(HTTPException) as exc_info:
            asyncio_run(login(body, response, FakeSession(None)))
        assert exc_info.value.status_code == 401


class TestLogoutEndpoint:
    def test_logout_clears_epm_token_cookie(self):
        response = Response()
        payload = asyncio_run(logout(response))
        assert payload["data"] is None
        cookies = [v.decode() for k, v in response.raw_headers if k == b"set-cookie"]
        assert any("epm_token" in c for c in cookies)
        assert any("Max-Age=0" in c for c in cookies)


class TestAuthMeEndpoint:
    def test_me_returns_user_envelope(self):
        payload = asyncio_run(me(make_user()))
        assert payload["data"]["username"] == "zubbyik"
        assert payload["data"]["role"] == "admin"


class TestChangePasswordEndpoint:
    def test_change_password_wrong_current_raises_400(self):
        body = ChangePasswordRequest(current_password="wrong", new_password="newpass123")
        session = FakeSession(make_user())
        with patch("app.routers.auth.pwd_context.verify", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                asyncio_run(change_password(body, make_user(), session))
        assert exc_info.value.status_code == 400

    def test_change_password_success_updates_hash(self):
        body = ChangePasswordRequest(current_password="oldpass", new_password="newpass123")
        user = make_user()
        session = AsyncMock()
        session.commit = AsyncMock()
        with patch("app.routers.auth.pwd_context.verify", return_value=True), \
             patch("app.routers.auth.pwd_context.hash", return_value="$2b$12$NEWHASH") as mock_hash:
            payload = asyncio_run(change_password(body, user, session))

        assert payload["data"]["message"] == "Password updated"
        mock_hash.assert_called_once_with("newpass123")
        session.add.assert_called_once_with(user)


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)