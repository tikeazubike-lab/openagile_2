# backend/tests/unit/test_admin_users.py
"""
Unit tests for Admin Users Router.
Tests CRUD operations for user management with admin-guarding.
All DB calls are mocked — no real database needed.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.deps import create_access_token, get_session, require_admin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_token(user_id: int = 1, role: str = "admin") -> str:
    return create_access_token(user_id=user_id, role=role)


def make_mock_user(user_id: int = 1, username: str = "zubbyik", role: str = "admin", name: str = "Zubby"):
    user = MagicMock()
    user.id = user_id
    user.username = username
    user.name = name
    user.role = role
    user.is_active = True
    user.deleted_at = None
    user.hashed_password = "$2b$12$hashedpassword"
    return user


# ===========================================================================
# Tests — direct dependency testing (no DB)
# ===========================================================================

class TestRequireAdminGuard:
    """Verify the require_admin dependency blocks non-admin users."""

    @pytest.mark.asyncio
    async def test_require_admin_blocks_readonly(self):
        from app.deps import require_admin
        mock_user = MagicMock()
        mock_user.role = "readonly"
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=mock_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_admin_allows_admin(self):
        from app.deps import require_admin
        mock_user = MagicMock()
        mock_user.role = "admin"
        result = await require_admin(current_user=mock_user)
        assert result == mock_user


class TestPasswordValidation:
    """Verify password strength validation in schemas."""

    def test_short_password_rejected(self):
        from app.routers.admin_users import UserCreate
        with pytest.raises(Exception):
            UserCreate(username="test", name="Test", password="short", role="readonly")

    def test_valid_password_accepted(self):
        from app.routers.admin_users import UserCreate
        user = UserCreate(username="test", name="Test", password="SecurePass123!", role="readonly")
        assert user.password == "SecurePass123!"

    def test_invalid_role_rejected(self):
        from app.routers.admin_users import UserCreate
        with pytest.raises(Exception):
            UserCreate(username="test", name="Test", password="SecurePass123!", role="superuser")

    def test_reset_password_short_rejected(self):
        from app.routers.admin_users import PasswordReset
        with pytest.raises(Exception):
            PasswordReset(new_password="abc")

    def test_reset_password_valid(self):
        from app.routers.admin_users import PasswordReset
        reset = PasswordReset(new_password="NewSecurePass456!")
        assert reset.new_password == "NewSecurePass456!"


# ===========================================================================
# Tests — endpoint integration tests with dependency overrides
# ===========================================================================

class TestAdminUsersEndpoints:
    """Test admin users endpoints with mocked DB via dependency overrides."""

    def test_list_users_as_admin(self):
        mock_user = make_mock_user()
        mock_db = MagicMock()

        async def mock_execute(*args, **kwargs):
            result = MagicMock()
            result.scalars.return_value.all.return_value = [mock_user]
            return result

        mock_db.execute = mock_execute

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_user

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.get("/api/v1/admin/users")

            assert response.status_code == 200
            body = response.json()
            assert "data" in body
            assert isinstance(body["data"], list)
            assert body["meta"]["total"] == 1
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_list_users_as_readonly(self):
        mock_user = make_mock_user(role="readonly")
        mock_db = MagicMock()

        async def mock_execute(*args, **kwargs):
            result = MagicMock()
            result.scalars.return_value.all.return_value = []
            return result

        mock_db.execute = mock_execute

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        # Override get_current_user to return readonly user
        # The real require_admin will check mock_user.role != "admin" and raise 403
        from app.deps import get_current_user as real_get_current_user
        app.dependency_overrides[real_get_current_user] = lambda: mock_user

        try:
            token = make_token(user_id=2, role="readonly")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.get("/api/v1/admin/users")

            assert response.status_code == 403
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_create_user_as_admin(self):
        mock_admin = make_mock_user()
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = None  # No duplicate
        mock_db.execute.return_value = result

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.post(
                "/api/v1/admin/users",
                json={
                    "username": "newuser",
                    "name": "New User",
                    "password": "SecurePass123!",
                    "role": "readonly",
                },
            )

            assert response.status_code == 201
            body = response.json()
            assert body["data"]["username"] == "newuser"
            assert body["data"]["name"] == "New User"
            assert body["data"]["role"] == "readonly"
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_create_user_duplicate_username(self):
        mock_admin = make_mock_user()
        existing = make_mock_user(username="existing")
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = existing
        mock_db.execute.return_value = result

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.post(
                "/api/v1/admin/users",
                json={
                    "username": "existing",
                    "name": "Another",
                    "password": "Pass123456!",
                    "role": "readonly",
                },
            )

            assert response.status_code == 409
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_update_user(self):
        mock_admin = make_mock_user()
        target_user = make_mock_user(user_id=2, username="target", name="Old Name", role="readonly")
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = target_user
        mock_db.execute.return_value = result

        async def mock_refresh(obj):
            obj.name = "Updated Name"
            obj.role = "admin"
            obj.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        mock_db.refresh = mock_refresh

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.patch(
                "/api/v1/admin/users/2",
                json={"name": "Updated Name", "role": "admin"},
            )

            assert response.status_code == 200
            body = response.json()
            assert body["data"]["name"] == "Updated Name"
            assert body["data"]["role"] == "admin"
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_reset_password(self):
        mock_admin = make_mock_user()
        target_user = make_mock_user(user_id=2, username="target")
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = target_user
        mock_db.execute.return_value = result

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.put(
                "/api/v1/admin/users/2/reset-password",
                json={"new_password": "NewSecurePass456!"},
            )

            assert response.status_code == 200
            body = response.json()
            assert body["data"]["id"] == 2
            assert "message" in body["data"]
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_delete_user(self):
        mock_admin = make_mock_user()
        target_user = make_mock_user(user_id=2, username="target")
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = target_user
        mock_db.execute.return_value = result

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.delete("/api/v1/admin/users/2")

            assert response.status_code == 200
            body = response.json()
            assert body["data"]["id"] == 2
            assert target_user.deleted_at is not None
            assert target_user.is_active is False
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)

    def test_cannot_delete_self(self):
        mock_admin = make_mock_user(user_id=1, username="zubbyik")
        mock_db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_admin
        mock_db.execute.return_value = result

        async def fake_session():
            yield mock_db

        original_session = app.dependency_overrides.get(get_session)
        original_admin = app.dependency_overrides.get(require_admin)
        app.dependency_overrides[get_session] = fake_session
        app.dependency_overrides[require_admin] = lambda: mock_admin

        try:
            token = make_token(role="admin")
            client = TestClient(app)
            client.cookies.set("epm_token", token)
            response = client.delete("/api/v1/admin/users/1")

            assert response.status_code == 400
        finally:
            if original_session is not None:
                app.dependency_overrides[get_session] = original_session
            else:
                app.dependency_overrides.pop(get_session, None)
            if original_admin is not None:
                app.dependency_overrides[require_admin] = original_admin
            else:
                app.dependency_overrides.pop(require_admin, None)
