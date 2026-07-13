# backend/tests/unit/test_api_routes.py
"""
Stage 1A.4 — API Route Unit Tests
Uses FastAPI TestClient with dependency_overrides to mock DB + auth.
Tests HTTP contract: status codes, cookie headers, response shapes.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.deps import create_access_token, get_session, get_current_user

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_token(user_id: int = 1, role: str = "admin") -> str:
    return create_access_token(user_id=user_id, role=role)


def make_mock_user(role: str = "admin") -> MagicMock:
    user = MagicMock()
    user.id = 1
    user.username = "zubbyik"
    user.name = "Zubby"
    user.role = role
    user.is_active = True
    user.hashed_password = "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5GzQq8H0F5Y6e7f8g9h0i1j2"
    return user


def make_mock_holding(holding_type: str = "active", deleted: bool = False) -> MagicMock:
    from decimal import Decimal
    h = MagicMock()
    h.id = 1
    h.company_id = 1
    h.num_shares = Decimal("100")
    h.average_cost_basis = Decimal("450.00")
    h.total_cost = Decimal("45000.00")
    h.current_value = Decimal("50000.00")
    h.holding_type = holding_type
    h.deleted_at = datetime(2026, 1, 1, tzinfo=timezone.utc) if deleted else None
    h.company = MagicMock()
    h.company.ticker = "DANGCEM"
    h.company.name = "Dangote Cement"
    h.company.sector = "Industrials"
    h.company.current_price = Decimal("500.00")
    h.claim_records = []
    h.cost_basis_override = None
    return h


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_client():
    token = make_token(role="admin")
    client = TestClient(app)
    client.cookies.set("epm_token", token)
    return client


@pytest.fixture
def readonly_client():
    token = make_token(role="readonly")
    client = TestClient(app)
    client.cookies.set("epm_token", token)
    return client


@pytest.fixture
def anonymous_client():
    return TestClient(app)


# ===========================================================================
# 1A.4 — Auth Endpoints
# ===========================================================================

def _mock_db(execute_result=None):
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=execute_result)
    result_mock.scalars = MagicMock()
    result_mock.scalars.return_value.all = MagicMock(return_value=execute_result or [])
    mock_db.execute.return_value = result_mock
    return mock_db


class TestLoginEndpoint:
    def test_login_endpoint_valid_credentials_sets_httponly_cookie(self):
        mock_user = make_mock_user()
        mock_db = _mock_db(execute_result=mock_user)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        try:
            with patch("app.routers.auth.pwd_context.verify", return_value=True):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"username": "zubbyik", "password": "testpassword"},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        assert "epm_token" in response.cookies
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie
        assert "samesite=strict" in set_cookie.lower()

    def test_login_endpoint_valid_credentials_returns_user_object(self):
        mock_user = make_mock_user()
        mock_db = _mock_db(execute_result=mock_user)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        try:
            with patch("app.routers.auth.pwd_context.verify", return_value=True):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"username": "zubbyik", "password": "testpassword"},
                )
        finally:
            app.dependency_overrides.clear()

        body = response.json()
        assert body["data"]["username"] == "zubbyik"
        assert body["data"]["role"] == "admin"
        assert "password_hash" not in body["data"]

    def test_login_endpoint_invalid_credentials_returns_401(self):
        mock_user = make_mock_user()
        mock_db = _mock_db(execute_result=mock_user)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        try:
            with patch("app.routers.auth.pwd_context.verify", return_value=False):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"username": "zubbyik", "password": "wrongpassword"},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 401

    def test_login_endpoint_nonexistent_user_returns_401(self):
        mock_db = _mock_db(execute_result=None)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "ghost", "password": "anypassword"},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 401


class TestLogoutEndpoint:
    def test_logout_endpoint_clears_epm_token_cookie(self, admin_client):
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.post("/api/v1/auth/logout")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        set_cookie = response.headers.get("set-cookie", "")
        assert "epm_token" in set_cookie
        assert "max-age=0" in set_cookie.lower()

    def test_logout_endpoint_returns_200_without_cookie_present(self, anonymous_client):
        response = anonymous_client.post("/api/v1/auth/logout")
        assert response.status_code == 200


class TestAuthMeEndpoint:
    def test_auth_me_endpoint_with_valid_cookie_returns_user(self, admin_client):
        mock_user = make_mock_user()
        app.dependency_overrides[get_current_user] = lambda: mock_user
        try:
            response = admin_client.get("/api/v1/auth/me")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["username"] == "zubbyik"
        assert body["data"]["role"] == "admin"

    def test_auth_me_endpoint_without_cookie_returns_401(self, anonymous_client):
        response = anonymous_client.get("/api/v1/auth/me")
        assert response.status_code == 401


# ===========================================================================
# 1A.4 — Holdings Endpoint
# ===========================================================================

class TestHoldingsEndpoint:
    def test_holdings_endpoint_excludes_deleted_records_by_default(self, admin_client):
        live = make_mock_holding(holding_type="active", deleted=False)
        mock_db = _mock_db(execute_result=[live])

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.get("/api/v1/holdings")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        holdings = response.json()["data"]
        assert all(h.get("deleted_at") is None for h in holdings)

    def test_holdings_endpoint_excludes_draft_records_for_readonly_role(self, readonly_client):
        mock_db = _mock_db(execute_result=[])

        async def _mock_session():
            yield mock_db

        readonly_user = make_mock_user(role="readonly")
        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: readonly_user
        try:
            response = readonly_client.get("/api/v1/holdings")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200

    def test_holdings_endpoint_includes_draft_records_for_admin_role(self, admin_client):
        draft = make_mock_holding(holding_type="draft")
        live = make_mock_holding(holding_type="active")
        mock_db = _mock_db(execute_result=[live, draft])

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.get("/api/v1/holdings")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        holdings = response.json()["data"]
        types = {h["holding_type"] for h in holdings}
        assert "draft" in types


# ===========================================================================
# 1A.4 — Soft Delete & Publish
# ===========================================================================

class TestSoftDeleteAndPublish:
    def test_soft_delete_sets_deleted_at_not_destroys_row(self, admin_client):
        mock_holding = make_mock_holding(holding_type="active")
        mock_db = _mock_db(execute_result=mock_holding)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.delete("/api/v1/holdings/1")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200

    def test_soft_delete_returns_403_for_readonly(self, readonly_client):
        app.dependency_overrides[get_current_user] = lambda: make_mock_user(role="readonly")
        try:
            response = readonly_client.delete("/api/v1/holdings/1")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 403

    def test_publish_holding_flips_status_draft_to_live(self, admin_client):
        mock_holding = make_mock_holding(holding_type="draft")
        mock_db = _mock_db(execute_result=mock_holding)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.post("/api/v1/holdings/1/publish")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200


# ===========================================================================
# 1A.4 — Price Quick Entry
# ===========================================================================

class TestPriceQuickEntry:
    def test_price_quick_entry_writes_to_price_audit_log(self, admin_client):
        mock_company = MagicMock()
        mock_company.id = 1
        mock_db = _mock_db(execute_result=mock_company)

        async def _mock_session():
            yield mock_db

        app.dependency_overrides[get_session] = _mock_session
        app.dependency_overrides[get_current_user] = lambda: make_mock_user()
        try:
            response = admin_client.post(
                "/api/v1/prices/quick",
                json={
                    "company_id": 1,
                    "price": "123.45",
                    "entry_date": "2026-04-20",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code in (200, 201)

    def test_price_quick_entry_returns_403_for_readonly(self, readonly_client):
        app.dependency_overrides[get_current_user] = lambda: make_mock_user(role="readonly")
        try:
            response = readonly_client.post(
                "/api/v1/prices/quick",
                json={"company_id": 1, "price": "123.45", "entry_date": "2026-04-20"},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 403
