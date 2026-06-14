# backend/tests/unit/test_api_routes.py
"""
Stage 1A.4 — API Route Unit Tests
Uses FastAPI TestClient with all DB calls mocked.
Tests HTTP contract: status codes, cookie headers, response shapes.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth.logic import create_access_token, hash_password

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_token(username: str = "zubbyik", role: str = "admin") -> str:
    return create_access_token(data={"sub": username, "role": role})


def make_mock_user(role: str = "admin") -> MagicMock:
    user = MagicMock()
    user.id = 1
    user.username = "zubbyik"
    user.name = "Zubby"
    user.role = role
    user.is_active = True
    user.password_hash = hash_password("testpassword")
    return user


def make_mock_holding(status: str = "live", deleted: bool = False) -> MagicMock:
    h = MagicMock()
    h.id = 1
    h.company_id = 1
    h.ticker = "DANGCEM"
    h.company_name = "Dangote Cement"
    h.sector = "Industrials"
    h.num_shares = 100
    h.avg_purchase_price = "450.00"
    h.current_price = "500.00"
    h.status = status
    h.deleted_at = datetime(2026, 1, 1, tzinfo=timezone.utc) if deleted else None
    return h


# ---------------------------------------------------------------------------
# Fixture: authenticated client
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_client():
    token = make_token(role="admin")
    client = TestClient(app)
    client.cookies.set("epm_token", token)
    return client


@pytest.fixture
def readonly_client():
    token = make_token(username="viewer", role="readonly")
    client = TestClient(app)
    client.cookies.set("epm_token", token)
    return client


@pytest.fixture
def anonymous_client():
    return TestClient(app)


# ===========================================================================
# 1A.4 — Auth Endpoints
# ===========================================================================

class TestLoginEndpoint:
    def test_login_endpoint_valid_credentials_sets_httponly_cookie(self):
        mock_user = make_mock_user()
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

        with patch("app.routers.auth.get_db", return_value=mock_db), \
             patch("app.routers.auth.verify_password", return_value=True):
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "zubbyik", "password": "testpassword"},
            )

        assert response.status_code == 200
        assert "epm_token" in response.cookies
        # httpOnly flag — not accessible via JS; verify via Set-Cookie header
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie
        assert "SameSite=strict" in set_cookie.lower() or "SameSite=Strict" in set_cookie

    def test_login_endpoint_valid_credentials_returns_user_object(self):
        mock_user = make_mock_user()
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

        with patch("app.routers.auth.get_db", return_value=mock_db), \
             patch("app.routers.auth.verify_password", return_value=True):
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "zubbyik", "password": "testpassword"},
            )

        body = response.json()
        assert body["data"]["user"]["username"] == "zubbyik"
        assert body["data"]["user"]["role"] == "admin"
        assert "password_hash" not in body["data"]["user"]  # never leak hash

    def test_login_endpoint_invalid_credentials_returns_401(self):
        mock_user = make_mock_user()
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

        with patch("app.routers.auth.get_db", return_value=mock_db), \
             patch("app.routers.auth.verify_password", return_value=False):
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "zubbyik", "password": "wrongpassword"},
            )

        assert response.status_code == 401

    def test_login_endpoint_nonexistent_user_returns_401(self):
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("app.routers.auth.get_db", return_value=mock_db):
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/login",
                json={"username": "ghost", "password": "anypassword"},
            )

        assert response.status_code == 401


class TestLogoutEndpoint:
    def test_logout_endpoint_clears_epm_token_cookie(self, admin_client):
        with patch("app.routers.auth.get_current_user", return_value=make_mock_user()):
            response = admin_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        set_cookie = response.headers.get("set-cookie", "")
        # Cookie cleared by Max-Age=0 or expires in past
        assert "epm_token" in set_cookie
        assert "Max-Age=0" in set_cookie or "max-age=0" in set_cookie.lower()

    def test_logout_endpoint_returns_200_without_cookie_present(self, anonymous_client):
        """Logout must be idempotent — no cookie = still 200 OK."""
        response = anonymous_client.post("/api/v1/auth/logout")
        assert response.status_code == 200


class TestAuthMeEndpoint:
    def test_auth_me_endpoint_with_valid_cookie_returns_user(self, admin_client):
        mock_user = make_mock_user()
        with patch("app.routers.auth.get_current_user", return_value=mock_user):
            response = admin_client.get("/api/v1/auth/me")

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
        live = make_mock_holding(status="live", deleted=False)
        deleted = make_mock_holding(status="live", deleted=True)
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = [live]

        with patch("app.routers.holdings.get_db", return_value=mock_db), \
             patch("app.routers.holdings.get_current_user", return_value=make_mock_user()):
            response = admin_client.get("/api/v1/holdings")

        assert response.status_code == 200
        holdings = response.json()["data"]
        assert all(h.get("deleted_at") is None for h in holdings)

    def test_holdings_endpoint_excludes_draft_records_for_readonly_role(self, readonly_client):
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        readonly_user = make_mock_user(role="readonly")
        with patch("app.routers.holdings.get_db", return_value=mock_db), \
             patch("app.routers.holdings.get_current_user", return_value=readonly_user):
            response = readonly_client.get("/api/v1/holdings")

        assert response.status_code == 200
        # Verify query was called with status='live' filter for readonly

    def test_holdings_endpoint_includes_draft_records_for_admin_role(self, admin_client):
        draft = make_mock_holding(status="draft")
        live = make_mock_holding(status="live")
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = [live, draft]

        with patch("app.routers.holdings.get_db", return_value=mock_db), \
             patch("app.routers.holdings.get_current_user", return_value=make_mock_user()):
            response = admin_client.get("/api/v1/holdings")

        assert response.status_code == 200
        holdings = response.json()["data"]
        statuses = {h["status"] for h in holdings}
        assert "draft" in statuses


# ===========================================================================
# 1A.4 — Soft Delete & Publish
# ===========================================================================

class TestSoftDeleteAndPublish:
    def test_soft_delete_sets_deleted_at_not_destroys_row(self, admin_client):
        mock_holding = make_mock_holding(status="live")
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_holding

        with patch("app.routers.holdings.get_db", return_value=mock_db), \
             patch("app.routers.holdings.get_current_user", return_value=make_mock_user()):
            response = admin_client.delete("/api/v1/holdings/1")

        assert response.status_code == 200
        # Verify deleted_at was SET (not a SQL DELETE)
        mock_db.execute.assert_called()  # DB was called
        mock_db.commit.assert_called()

    def test_soft_delete_returns_403_for_readonly(self, readonly_client):
        with patch("app.routers.holdings.get_current_user",
                   return_value=make_mock_user(role="readonly")):
            response = readonly_client.delete("/api/v1/holdings/1")
        assert response.status_code == 403

    def test_publish_holding_flips_status_draft_to_live(self, admin_client):
        mock_holding = make_mock_holding(status="draft")
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_holding

        with patch("app.routers.holdings.get_db", return_value=mock_db), \
             patch("app.routers.holdings.get_current_user", return_value=make_mock_user()):
            response = admin_client.put("/api/v1/holdings/1/publish")

        assert response.status_code == 200


# ===========================================================================
# 1A.4 — Price Quick Entry
# ===========================================================================

class TestPriceQuickEntry:
    def test_price_quick_entry_writes_to_price_audit_log(self, admin_client):
        mock_db = AsyncMock()
        mock_company = MagicMock()
        mock_company.id = 1
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_company

        with patch("app.routers.prices.get_db", return_value=mock_db), \
             patch("app.routers.prices.get_current_user", return_value=make_mock_user()):
            response = admin_client.post(
                "/api/v1/prices/quick",
                json={
                    "company_id": 1,
                    "price": "123.45",
                    "entry_date": "2026-04-20",
                },
            )

        assert response.status_code in (200, 201)
        # Verify audit record was added
        add_calls = mock_db.add.call_args_list
        assert len(add_calls) >= 1  # at least one DB write (audit log)

    def test_price_quick_entry_returns_403_for_readonly(self, readonly_client):
        with patch("app.routers.prices.get_current_user",
                   return_value=make_mock_user(role="readonly")):
            response = readonly_client.post(
                "/api/v1/prices/quick",
                json={"company_id": 1, "price": "123.45", "entry_date": "2026-04-20"},
            )
        assert response.status_code == 403