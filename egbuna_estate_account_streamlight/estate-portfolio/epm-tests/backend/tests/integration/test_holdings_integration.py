# backend/tests/integration/test_holdings_integration.py
"""
Stage 2C — Holdings Integration Tests
Full CRUD, draft/live workflow, soft delete, restore, role enforcement.
All changes rolled back after each test via conftest.py savepoint fixture.
"""
import pytest
from httpx import AsyncClient


class TestHoldingsIntegration:

    # -----------------------------------------------------------------------
    # Create
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_create_holding_defaults_to_draft_status(
        self, admin_http_client: AsyncClient, test_company
    ):
        response = await admin_http_client.post(
            "/api/v1/holdings",
            json={
                "company_id": test_company.id,
                "num_shares": 200,
                "avg_purchase_price": "123.45",
            },
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_holding_blocked_for_readonly(
        self, readonly_http_client: AsyncClient, test_company
    ):
        response = await readonly_http_client.post(
            "/api/v1/holdings",
            json={
                "company_id": test_company.id,
                "num_shares": 100,
                "avg_purchase_price": "100.00",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_duplicate_company_holding_is_rejected_by_db_constraint(
        self, admin_http_client: AsyncClient, test_live_holding, test_company
    ):
        """UNIQUE(company_id) must prevent two open positions in same company."""
        response = await admin_http_client.post(
            "/api/v1/holdings",
            json={
                "company_id": test_company.id,  # already has a live holding
                "num_shares": 50,
                "avg_purchase_price": "200.00",
            },
        )
        assert response.status_code in (400, 409, 422)

    # -----------------------------------------------------------------------
    # Publish workflow
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_publish_holding_changes_status_to_live_in_db(
        self, admin_http_client: AsyncClient, test_draft_holding, db_session
    ):
        response = await admin_http_client.put(
            f"/api/v1/holdings/{test_draft_holding.id}/publish"
        )
        assert response.status_code == 200

        await db_session.refresh(test_draft_holding)
        assert test_draft_holding.status == "live"

    @pytest.mark.asyncio
    async def test_publish_holding_blocked_for_readonly(
        self, readonly_http_client: AsyncClient, test_draft_holding
    ):
        response = await readonly_http_client.put(
            f"/api/v1/holdings/{test_draft_holding.id}/publish"
        )
        assert response.status_code == 403

    # -----------------------------------------------------------------------
    # Soft delete
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_soft_delete_holding_sets_deleted_at_in_db(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        response = await admin_http_client.delete(
            f"/api/v1/holdings/{test_live_holding.id}"
        )
        assert response.status_code == 200

        await db_session.refresh(test_live_holding)
        assert test_live_holding.deleted_at is not None

    @pytest.mark.asyncio
    async def test_soft_deleted_holding_excluded_from_list(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        # Delete it first
        await admin_http_client.delete(f"/api/v1/holdings/{test_live_holding.id}")

        # Should not appear in list
        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200
        ids = [h["id"] for h in response.json()["data"]]
        assert test_live_holding.id not in ids

    # -----------------------------------------------------------------------
    # Restore
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_restore_holding_clears_deleted_at_in_db(
        self, admin_http_client: AsyncClient, test_live_holding, db_session
    ):
        # Soft delete first
        await admin_http_client.delete(f"/api/v1/holdings/{test_live_holding.id}")
        await db_session.refresh(test_live_holding)
        assert test_live_holding.deleted_at is not None

        # Restore
        response = await admin_http_client.put(
            f"/api/v1/holdings/{test_live_holding.id}/restore"
        )
        assert response.status_code == 200

        await db_session.refresh(test_live_holding)
        assert test_live_holding.deleted_at is None

    # -----------------------------------------------------------------------
    # Role-based visibility
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_readonly_role_cannot_see_draft_holdings_from_api(
        self, readonly_http_client: AsyncClient, test_draft_holding
    ):
        response = await readonly_http_client.get("/api/v1/holdings")
        assert response.status_code == 200
        ids = [h["id"] for h in response.json()["data"]]
        assert test_draft_holding.id not in ids

    @pytest.mark.asyncio
    async def test_admin_role_can_see_draft_holdings_from_api(
        self, admin_http_client: AsyncClient, test_draft_holding
    ):
        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200
        ids = [h["id"] for h in response.json()["data"]]
        assert test_draft_holding.id in ids

    # -----------------------------------------------------------------------
    # Response shape
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_holdings_response_contains_return_pct_field(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200
        holdings = response.json()["data"]
        if holdings:
            assert "return_pct" in holdings[0], "return_pct field missing from holdings response"

    @pytest.mark.asyncio
    async def test_holdings_monetary_fields_are_strings(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        response = await admin_http_client.get("/api/v1/holdings")
        holdings = response.json()["data"]
        for h in holdings:
            for field in ("avg_purchase_price", "current_price", "current_value", "cost_basis"):
                if field in h and h[field] is not None:
                    assert isinstance(h[field], str), (
                        f"Field {field} must be string, got {type(h[field])}"
                    )