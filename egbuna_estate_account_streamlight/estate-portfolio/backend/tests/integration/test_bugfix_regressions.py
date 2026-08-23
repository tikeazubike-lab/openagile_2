"""
Regression tests for three production bug fixes (HO-134).

| BUG-ID               | Covers                                                        |
|----------------------|---------------------------------------------------------------|
| BUG-TZ-NAIVE-001     | Aware datetime written to naive TIMESTAMP columns (4 sites)   |
| BUG-HOLDING-STATUS-001 | update_holding returned non-existent h.status                |
| BUG-PDF-UPLOAD-500-001 | /prices/upload-pdf 500 on unparseable PDFs                   |

Each test fails on the pre-fix code (500 / AttributeError) and passes here.
"""
import io

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestTzNaiveRegression:
    """BUG-TZ-NAIVE-001 — aware datetime into naive TIMESTAMP WITHOUT TIME ZONE."""

    @pytest.mark.asyncio
    async def test_change_password_stores_naive_updated_at(
        self, admin_http_client: AsyncClient
    ):
        me = await admin_http_client.get("/api/v1/auth/me")
        username = me.json()["data"]["username"]

        response = await admin_http_client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "testpass123", "new_password": "NewSecurePass456!"},
        )
        assert response.status_code == 200

        # Re-login with the new password proves the hash was actually updated
        login_resp = await admin_http_client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "NewSecurePass456!"},
        )
        assert login_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_holding_soft_delete_sets_deleted_at(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        response = await admin_http_client.delete(f"/api/v1/holdings/{test_live_holding.id}")
        assert response.status_code == 200
        await db_session.refresh(test_live_holding)
        assert test_live_holding.deleted_at is not None

    @pytest.mark.asyncio
    async def test_registrar_soft_delete_succeeds(
        self, admin_http_client: AsyncClient, db_session
    ):
        from app.models import Registrar
        reg = Registrar(name="TZ Naive Registrar")
        db_session.add(reg)
        await db_session.flush()

        response = await admin_http_client.delete(f"/api/v1/registrars/{reg.id}")
        assert response.status_code == 200
        await db_session.refresh(reg)
        assert reg.deleted_at is not None

    @pytest.mark.asyncio
    async def test_user_soft_delete_succeeds(
        self, admin_http_client: AsyncClient, db_session
    ):
        from passlib.context import CryptContext
        from app.models import User
        pwd = CryptContext(schemes=["bcrypt"])
        user = User(
            username="tz_naive_user",
            name="TZ Naive User",
            hashed_password=pwd.hash("password123"),
            role="readonly",
            is_active=True,
        )
        db_session.add(user)
        await db_session.flush()

        response = await admin_http_client.delete(f"/api/v1/admin/users/{user.id}")
        assert response.status_code == 200
        await db_session.refresh(user)
        assert user.deleted_at is not None


class TestHoldingStatusRegression:
    """BUG-HOLDING-STATUS-001 — update_holding referenced h.status."""

    @pytest.mark.asyncio
    async def test_update_holding_returns_holding_type_as_status(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        response = await admin_http_client.patch(
            f"/api/v1/holdings/{test_live_holding.id}",
            json={"num_shares": 750, "holding_type": "claim"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert float(data["shares"]) == 750.0
        assert data["holding_type"] == "claim"
        assert data["status"] == "claim"


class TestPdfUploadRegression:
    """BUG-PDF-UPLOAD-500-001 — upload-pdf must 422, not 500, on bad PDFs."""

    @pytest.mark.asyncio
    async def test_upload_pdf_returns_422_for_unparseable_pdf(
        self, admin_http_client: AsyncClient
    ):
        fake_pdf = b"%PDF-1.4 fake content"
        files = {"file": ("ngx_daily.pdf", io.BytesIO(fake_pdf), "application/pdf")}
        response = await admin_http_client.post("/api/v1/prices/upload-pdf", files=files)
        assert response.status_code == 422