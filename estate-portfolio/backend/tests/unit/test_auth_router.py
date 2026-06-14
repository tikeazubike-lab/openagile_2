import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import Response
from fastapi.exceptions import HTTPException

from app.routers.auth import login, logout, me, LoginRequest


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


def test_login_sets_cookie_and_returns_user_envelope():
    user = SimpleNamespace(
        id=1,
        username="zubbyik",
        name="Zubby",
        role="admin",
        is_active=True,
        deleted_at=None,
        hashed_password="$2b$12$5JOVNxT0x5j0g8iM4d0PO.FSnC7XXIQK5lLylJ.gUvVf2fd2A4J3K",
    )
    response = Response()
    body = LoginRequest(username="zubbyik", password="testpassword")
    with patch("app.routers.auth.pwd_context.verify", return_value=True):
        payload = asyncio.run(login(body, response, FakeSession(user)))

    assert payload["data"]["username"] == "zubbyik"
    assert "epm_token=" in response.headers.get("set-cookie", "")


def test_login_rejects_invalid_credentials():
    user = SimpleNamespace(
        id=1,
        username="zubbyik",
        name="Zubby",
        role="admin",
        is_active=True,
        deleted_at=None,
        hashed_password="$2b$12$5JOVNxT0x5j0g8iM4d0PO.FSnC7XXIQK5lLylJ.gUvVf2fd2A4J3X",
    )
    response = Response()
    body = LoginRequest(username="zubbyik", password="wrongpassword")

    try:
        with patch("app.routers.auth.pwd_context.verify", return_value=False):
            asyncio.run(login(body, response, FakeSession(user)))
        assert False, "Expected invalid credentials"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_logout_returns_success_envelope():
    response = Response()
    payload = asyncio.run(logout(response))
    assert payload["data"]["message"] == "Logged out"


def test_me_returns_current_user_envelope():
    user = SimpleNamespace(id=1, username="zubbyik", name="Zubby", role="admin")
    payload = asyncio.run(me(user))
    assert payload["data"]["username"] == "zubbyik"
    assert payload["data"]["role"] == "admin"
