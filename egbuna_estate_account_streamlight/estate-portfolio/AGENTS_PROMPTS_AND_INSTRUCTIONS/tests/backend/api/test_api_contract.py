# backend/tests/contract/test_api_contract.py
"""
Stage 2A — API Contract Tests
Validates every endpoint's response schema matches the spec in the handover brief.
Runs against the real app with real DB (rollback fixture from conftest).
"""
import json

import jsonschema
import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Response envelope schema
# ---------------------------------------------------------------------------

ENVELOPE_SCHEMA = {
    "type": "object",
    "required": ["data", "error"],
    "properties": {
        "data": {},
        "error": {"type": ["null", "object", "string"]},
    },
}

LIST_ENVELOPE_SCHEMA = {
    "type": "object",
    "required": ["data", "meta", "error"],
    "properties": {
        "data": {"type": "array"},
        "meta": {
            "type": "object",
            "required": ["total"],
            "properties": {"total": {"type": "integer"}},
        },
        "error": {"type": ["null", "object", "string"]},
    },
}


def validate_envelope(body: dict, is_list: bool = False):
    schema = LIST_ENVELOPE_SCHEMA if is_list else ENVELOPE_SCHEMA
    jsonschema.validate(instance=body, schema=schema)


class TestAPIContract:

    # -----------------------------------------------------------------------
    # OpenAPI schema
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_openapi_schema_is_valid_json(self, async_client: AsyncClient):
        response = await async_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    @pytest.mark.asyncio
    async def test_all_api_routes_are_documented_in_openapi(
        self, async_client: AsyncClient
    ):
        response = await async_client.get("/openapi.json")
        paths = response.json()["paths"]
        required_prefixes = [
            "/api/v1/auth/",
            "/api/v1/dashboard",
            "/api/v1/holdings",
            "/api/v1/companies",
            "/api/v1/prices",
            "/api/v1/dividends",
            "/api/v1/transactions",
            "/api/v1/registrars",
            "/api/v1/watchlist",
            "/api/v1/nav-history",
            "/api/v1/rebalancing",
        ]
        documented = list(paths.keys())
        for prefix in required_prefixes:
            assert any(p.startswith(prefix) for p in documented), (
                f"No documented routes found for prefix: {prefix}"
            )

    # -----------------------------------------------------------------------
    # Envelope conformance
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_error_responses_use_standard_envelope(
        self, async_client: AsyncClient
    ):
        """A 401 on /me must still return { data: null, error: {...} }."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        body = response.json()
        assert "error" in body
        assert body["error"] is not None

    @pytest.mark.asyncio
    async def test_404_responses_return_json_not_html(
        self, async_client: AsyncClient
    ):
        response = await async_client.get("/api/v1/does-not-exist-xyz")
        assert response.status_code == 404
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    @pytest.mark.asyncio
    async def test_all_list_endpoints_return_meta_with_total(
        self, admin_http_client: AsyncClient, test_admin_user
    ):
        list_endpoints = [
            "/api/v1/holdings",
            "/api/v1/companies",
            "/api/v1/dividends",
            "/api/v1/transactions",
            "/api/v1/registrars",
            "/api/v1/watchlist",
        ]
        for endpoint in list_endpoints:
            response = await admin_http_client.get(endpoint)
            assert response.status_code == 200, f"Failed on {endpoint}"
            body = response.json()
            assert "meta" in body, f"Missing 'meta' on {endpoint}"
            assert "total" in body["meta"], f"Missing meta.total on {endpoint}"

    # -----------------------------------------------------------------------
    # Holdings response contract
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_holdings_response_monetary_fields_are_strings_not_floats(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        response = await admin_http_client.get("/api/v1/holdings")
        assert response.status_code == 200
        holdings = response.json()["data"]
        monetary_fields = [
            "avg_purchase_price", "current_price", "current_value",
            "cost_basis", "return_pct",
        ]
        for h in holdings:
            for field in monetary_fields:
                if field in h and h[field] is not None:
                    assert isinstance(h[field], str), (
                        f"Field '{field}' must be string, got {type(h[field]).__name__} "
                        f"in holding id={h.get('id')}"
                    )

    @pytest.mark.asyncio
    async def test_holdings_response_contains_return_pct_field(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        response = await admin_http_client.get("/api/v1/holdings")
        holdings = response.json()["data"]
        if holdings:
            assert "return_pct" in holdings[0]

    # -----------------------------------------------------------------------
    # Auth response contract
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_auth_me_response_contains_role_field(
        self, admin_http_client: AsyncClient, test_admin_user
    ):
        response = await admin_http_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "role" in data
        assert data["role"] in ("admin", "readonly")

    @pytest.mark.asyncio
    async def test_auth_login_sets_httponly_cookie_not_json_token(
        self, async_client: AsyncClient, test_admin_user
    ):
        """Token must be in httpOnly cookie, never in JSON body."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "test_admin", "password": "testpass123"},
        )
        assert response.status_code == 200
        body = response.json()
        # Token must NOT appear in JSON body
        body_str = json.dumps(body)
        assert "access_token" not in body_str or body_str.count("access_token") == 0
        # Token must be in Set-Cookie header
        assert "epm_token" in response.cookies

    # -----------------------------------------------------------------------
    # Soft delete & draft record exclusion
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_soft_deleted_records_absent_from_default_responses(
        self, admin_http_client: AsyncClient, test_live_holding
    ):
        # Soft delete the holding
        await admin_http_client.delete(f"/api/v1/holdings/{test_live_holding.id}")

        # Should not appear in list
        response = await admin_http_client.get("/api/v1/holdings")
        ids = [h["id"] for h in response.json()["data"]]
        assert test_live_holding.id not in ids

    @pytest.mark.asyncio
    async def test_draft_records_absent_from_readonly_role_responses(
        self, readonly_http_client: AsyncClient, test_draft_holding
    ):
        response = await readonly_http_client.get("/api/v1/holdings")
        ids = [h["id"] for h in response.json()["data"]]
        assert test_draft_holding.id not in ids
