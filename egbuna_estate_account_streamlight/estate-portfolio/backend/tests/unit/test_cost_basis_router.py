"""
Unit tests for Cost Basis router (F-COST-BASIS).
Uses FastAPI TestClient with dependency_overrides to mock DB + auth.
"""
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_session, get_current_user


def make_mock_user(role="admin"):
    user = MagicMock()
    user.id = 1
    user.username = "test_admin"
    user.name = "Test Admin"
    user.role = role
    user.is_active = True
    return user


def make_mock_company(ticker="DANGCEM", name="Dangote Cement Plc", sector="Industrial Goods", status="listed"):
    c = MagicMock()
    c.id = 1
    c.ticker = ticker
    c.name = name
    c.sector = sector
    c.status = status
    c.current_price = None
    c.last_price_update = None
    return c


class MockAsyncSession:
    """Stand-in for AsyncSession with configurable execute results."""

    def __init__(self, companies=None):
        self._companies = companies or []
        self._execute_call_count = 0
        self.added = []
        self.flushed = False
        self.committed = False

    async def execute(self, *args, **kwargs):
        self._execute_call_count += 1
        result = MagicMock()
        result.scalars.return_value.all.return_value = self._companies
        result.scalar_one_or_none.return_value = self._companies[0] if self._companies else None
        result.fetchall.return_value = self._companies
        return result

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True
        for obj in self.added:
            if hasattr(obj, 'id') and obj.id is None:
                obj.id = hash(obj) % 10000

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        obj.id = getattr(obj, 'id', None) or 1

    async def rollback(self):
        pass

    async def close(self):
        pass


_session_container = [MockAsyncSession()]

async def _override_session():
    yield _session_container[0]

def _get_mock_db():
    return _session_container[0]

def _set_companies(companies):
    _session_container[0]._companies = companies


@pytest.fixture(autouse=True)
def setup_mocks():
    _session_container[0] = MockAsyncSession()
    app.dependency_overrides[get_session] = _override_session
    app.dependency_overrides[get_current_user] = lambda: make_mock_user()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():
    return TestClient(app)


@pytest.fixture
def readonly_client():
    app.dependency_overrides[get_current_user] = lambda: make_mock_user(role="readonly")
    yield TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: make_mock_user()


class TestQuickCostBasis:
    def test_creates_holding_with_existing_ticker(self, admin_client):
        _set_companies([make_mock_company("DANGCEM", "Dangote Cement Plc")])

        response = admin_client.post(
            "/api/v1/cost-basis/quick",
            data={
                "ticker": "DANGCEM",
                "avg_purchase_price": "245.50",
                "quantity": "500",
                "purchase_date": "2024-01-15",
            },
        )

        assert response.status_code == 201
        body = response.json()["data"]
        assert body["ticker"] == "DANGCEM"
        assert body["avg_purchase_price"] == "245.50"
        assert body["quantity"] == 500.0
        assert body["holding_type"] == "active"
        assert _get_mock_db().committed

    def test_creates_claim_for_delisted_company(self, admin_client):
        _set_companies([make_mock_company("DELISTED", "Old Delisted Co", status="delisted")])

        response = admin_client.post(
            "/api/v1/cost-basis/quick",
            data={
                "ticker": "DELISTED",
                "avg_purchase_price": "100.00",
                "quantity": "200",
                "purchase_date": "2023-06-01",
            },
        )

        assert response.status_code == 201
        body = response.json()["data"]
        assert body["holding_type"] == "claim"

    def test_creates_new_company_when_ticker_not_found(self, admin_client):
        _set_companies([])

        response = admin_client.post(
            "/api/v1/cost-basis/quick",
            data={
                "ticker": "NEWCO",
                "company_name": "New Company Ltd",
                "avg_purchase_price": "50.00",
                "quantity": "100",
                "purchase_date": "2024-06-01",
            },
        )

        assert response.status_code == 201
        body = response.json()["data"]
        assert body["ticker"] == "NEWCO"
        assert body["holding_type"] == "active"

    def test_rejects_invalid_price(self, admin_client):
        response = admin_client.post(
            "/api/v1/cost-basis/quick",
            data={"ticker": "TEST", "avg_purchase_price": "-10", "quantity": "100"},
        )
        assert response.status_code == 422

    def test_requires_admin(self, readonly_client):
        response = readonly_client.post(
            "/api/v1/cost-basis/quick",
            data={"ticker": "TEST", "avg_purchase_price": "10", "quantity": "100"},
        )
        assert response.status_code == 403


class TestBulkCsvCostBasis:
    @patch("app.routers.cost_basis._resolve_company")
    def test_preview_returns_valid_and_error_rows(self, mock_resolve, admin_client):
        mock_resolve.return_value = make_mock_company("DANGCEM", "Dangote Cement Plc")
        _set_companies([make_mock_company("DANGCEM")])

        csv_content = (
            "ticker,company_name,avg_purchase_price,quantity,purchase_date\n"
            "DANGCEM,Dangote Cement Plc,245.50,500,2024-01-15\n"
            ",,abc,0,invalid-date\n"
        )
        response = admin_client.post(
            "/api/v1/cost-basis/bulk-csv",
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
            data={"commit": "false"},
        )

        assert response.status_code == 201
        body = response.json()["data"]
        assert body["valid"] == 1
        assert body["errors"] == 1
        assert body["committed"] is False

    @patch("app.routers.cost_basis._resolve_company")
    @patch("app.routers.cost_basis._create_holding")
    def test_commit_creates_holdings(self, mock_create, mock_resolve, admin_client):
        mock_resolve.return_value = make_mock_company("DANGCEM", "Dangote Cement Plc")
        mock_create.return_value = MagicMock(
            holding_type="active",
            id=1,
            company_id=1,
            average_cost_basis=Decimal("245.50"),
            num_shares=Decimal("500"),
            purchase_date=date(2024, 1, 15),
        )

        csv_content = (
            "ticker,company_name,avg_purchase_price,quantity,purchase_date\n"
            "DANGCEM,Dangote Cement Plc,245.50,500,2024-01-15\n"
        )
        response = admin_client.post(
            "/api/v1/cost-basis/bulk-csv",
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
            data={"commit": "true"},
        )

        assert response.status_code == 201
        body = response.json()["data"]
        assert body["summary"]["active_holdings_created"] == 1

    def test_rejects_missing_columns(self, admin_client):
        csv_content = "ticker,foo\nDANGCEM,bar\n"
        response = admin_client.post(
            "/api/v1/cost-basis/bulk-csv",
            files={"file": ("bad.csv", csv_content.encode(), "text/csv")},
            data={"commit": "false"},
        )
        assert response.status_code == 422

    def test_requires_admin(self, readonly_client):
        csv_content = "ticker,avg_purchase_price,quantity,purchase_date\nTEST,10,1,2024-01-01\n"
        response = readonly_client.post(
            "/api/v1/cost-basis/bulk-csv",
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
            data={"commit": "false"},
        )
        assert response.status_code == 403


class TestListCostBasis:
    def test_lists_cost_basis_records(self, admin_client):
        _set_companies([make_mock_company("DANGCEM")])

        response = admin_client.get("/api/v1/cost-basis")
        assert response.status_code == 200


class TestDownloadTemplate:
    def test_download_template(self, admin_client):
        response = admin_client.get("/api/v1/cost-basis/download-template")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_requires_admin(self, readonly_client):
        response = readonly_client.get("/api/v1/cost-basis/download-template")
        assert response.status_code == 403
