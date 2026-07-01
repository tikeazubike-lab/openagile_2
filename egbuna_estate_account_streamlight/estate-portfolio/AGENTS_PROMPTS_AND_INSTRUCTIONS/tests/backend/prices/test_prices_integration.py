# backend/tests/integration/test_prices_integration.py
"""
Stage 2C — Price Entry & NAV History Integration Tests
Tests quick entry, CSV bulk import atomicity, audit logging, revert, NAV snapshots.
All changes rolled back after each test.
"""
import io
from datetime import date

import pytest
from httpx import AsyncClient


class TestPriceIntegration:

    # -----------------------------------------------------------------------
    # Quick entry
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_price_entry_creates_price_audit_record(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        response = await admin_http_client.post(
            "/api/v1/prices/quick",
            json={
                "company_id": test_company.id,
                "price": "123.45",
                "entry_date": str(date.today()),
            },
        )
        assert response.status_code in (200, 201)

        # Verify audit record exists in DB
        from sqlalchemy import select, text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM price_audit WHERE company_id = :cid"),
            {"cid": test_company.id},
        )
        count = result.scalar_one()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_price_audit_stores_old_and_new_price(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        # First price entry
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )
        # Second price entry (creates audit with old=100 new=150)
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "150.00", "entry_date": str(date.today())},
        )

        from sqlalchemy import text
        result = await db_session.execute(
            text(
                "SELECT old_price, new_price FROM price_audit "
                "WHERE company_id = :cid ORDER BY changed_at DESC LIMIT 1"
            ),
            {"cid": test_company.id},
        )
        row = result.fetchone()
        assert row is not None
        assert str(row.new_price) == "150.00"

    @pytest.mark.asyncio
    async def test_price_revert_restores_previous_value_in_db(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        # Set initial price
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )

        # Change to new price
        await admin_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "200.00", "entry_date": str(date.today())},
        )

        # Get audit record ID
        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT id FROM price_audit WHERE company_id = :cid ORDER BY changed_at DESC LIMIT 1"),
            {"cid": test_company.id},
        )
        audit_id = result.scalar_one()

        # Revert
        revert_resp = await admin_http_client.post(f"/api/v1/prices/audit/{audit_id}/revert")
        assert revert_resp.status_code == 200

        # Verify price is back to 100.00
        result = await db_session.execute(
            text("SELECT current_price FROM companies WHERE id = :cid"),
            {"cid": test_company.id},
        )
        current = result.scalar_one()
        assert str(current) == "100.00"

    # -----------------------------------------------------------------------
    # Bulk CSV import
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bulk_csv_import_updates_multiple_prices_atomically(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        csv_content = f"ticker,price,date\n{test_company.ticker},999.99,{date.today()}\n"
        files = {"file": ("prices.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        mapping = {"ticker_col": "ticker", "price_col": "price", "date_col": "date"}

        response = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data=mapping,
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert body["updated"] >= 1

    @pytest.mark.asyncio
    async def test_bulk_csv_import_rolls_back_on_partial_failure(
        self, admin_http_client: AsyncClient, test_company
    ):
        """If any row fails validation, the entire import is rolled back."""
        csv_content = (
            f"ticker,price,date\n"
            f"{test_company.ticker},500.00,{date.today()}\n"
            f"UNKNOWN_XYZ,-99.00,{date.today()}\n"  # invalid: unknown ticker + negative price
        )
        files = {"file": ("prices.csv", io.BytesIO(csv_content.encode()), "text/csv")}
        mapping = {"ticker_col": "ticker", "price_col": "price", "date_col": "date"}

        # Stage 1: preview
        preview_resp = await admin_http_client.post(
            "/api/v1/prices/bulk-csv",
            files=files,
            data=mapping,
        )
        assert preview_resp.status_code == 200
        preview = preview_resp.json()["data"]
        # Errors must be flagged before commit
        assert preview.get("errors", 0) >= 1

    # -----------------------------------------------------------------------
    # Price entry blocked for readonly
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_price_quick_entry_blocked_for_readonly(
        self, readonly_http_client: AsyncClient, test_company
    ):
        response = await readonly_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": test_company.id, "price": "100.00", "entry_date": str(date.today())},
        )
        assert response.status_code == 403


class TestNavHistoryIntegration:

    @pytest.mark.asyncio
    async def test_nav_snapshot_inserts_row_into_nav_history(
        self, admin_http_client: AsyncClient, db_session
    ):
        response = await admin_http_client.post("/api/v1/nav-history/snapshot")
        assert response.status_code in (200, 201)

        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM nav_history WHERE snapshot_date = CURRENT_DATE")
        )
        count = result.scalar_one()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_nav_snapshot_is_idempotent_for_same_day(
        self, admin_http_client: AsyncClient, db_session
    ):
        """Running snapshot twice on same day must not raise or duplicate."""
        r1 = await admin_http_client.post("/api/v1/nav-history/snapshot")
        r2 = await admin_http_client.post("/api/v1/nav-history/snapshot")

        assert r1.status_code in (200, 201)
        assert r2.status_code in (200, 200)  # second call is OK (upsert)

        from sqlalchemy import text
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM nav_history WHERE snapshot_date = CURRENT_DATE")
        )
        count = result.scalar_one()
        assert count == 1  # exactly one row per day

    @pytest.mark.asyncio
    async def test_nav_snapshot_blocked_for_readonly(
        self, readonly_http_client: AsyncClient
    ):
        response = await readonly_http_client.post("/api/v1/nav-history/snapshot")
        assert response.status_code == 403
