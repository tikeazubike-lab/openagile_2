# backend/tests/integration/test_auth_integration.py
"""
Stage 2C — Auth Integration Tests
Full request → handler → real Postgres → response path.
All DB changes wrapped in rollback fixture (see conftest.py).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestAuthIntegration:

    @pytest.mark.asyncio
    async def test_login_creates_session_cookie_against_real_db(
        self, async_client: AsyncClient, test_admin_user
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "epm_token" in response.cookies
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie
        assert "SameSite=Strict" in set_cookie or "samesite=strict" in set_cookie.lower()

    @pytest.mark.asyncio
    async def test_login_rejects_wrong_password_against_real_db(
        self, async_client: AsyncClient, test_admin_user
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "WRONGPASSWORD"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_rejects_nonexistent_user(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "ghost_user_xyz", "password": "anypass"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_clears_cookie_verified_by_subsequent_me_call(
        self, async_client: AsyncClient, test_admin_user
    ):
        # Log in first
        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "testpass123"},
        )
        assert login_resp.status_code == 200

        # Now log out
        logout_resp = await async_client.post("/api/v1/auth/logout")
        assert logout_resp.status_code == 200

        # Cookie should be cleared — /me should now 401
        me_resp = await async_client.get("/api/v1/auth/me")
        assert me_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_me_returns_correct_role_from_db(
        self, admin_http_client: AsyncClient, test_admin_user
    ):
        response = await admin_http_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["role"] == "admin"
        assert body["data"]["username"] == "test_admin"

    @pytest.mark.asyncio
    async def test_auth_me_readonly_user_returns_readonly_role(
        self, user_http_client: AsyncClient, test_readonly_user
    ):
        response = await user_http_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        assert response.json()["data"]["role"] == "readonly"

    @pytest.mark.asyncio
    async def test_change_password_updates_hash_in_db(
        self, admin_http_client: AsyncClient, test_admin_user, db_session
    ):
        response = await admin_http_client.put(
            "/api/v1/auth/change-password",
            json={
                "current_password": "testpass123",
                "new_password": "NewSecurePass456!",
            },
        )
        assert response.status_code == 200

        # Verify new password works for login
        from app.auth.logic import verify_password
        await db_session.refresh(test_admin_user)
        assert verify_password("NewSecurePass456!", test_admin_user.password_hash)
        assert not verify_password("testpass123", test_admin_user.password_hash)

    @pytest.mark.asyncio
    async def test_change_password_rejected_with_wrong_current_password(
        self, admin_http_client: AsyncClient, test_admin_user
    ):
        response = await admin_http_client.put(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrongcurrentpass",
                "new_password": "NewPass789!",
            },
        )
        assert response.status_code in (400, 401)

    @pytest.mark.asyncio
    async def test_change_password_blocked_for_readonly_role(
        self, user_http_client: AsyncClient, test_readonly_user
    ):
        """Readonly users cannot change their password via API."""
        response = await user_http_client.put(
            "/api/v1/auth/change-password",
            json={
                "current_password": "viewpass123",
                "new_password": "NewPass789!",
            },
        )
        assert response.status_code == 403