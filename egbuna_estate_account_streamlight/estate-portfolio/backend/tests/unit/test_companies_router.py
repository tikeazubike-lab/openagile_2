"""
Unit tests for Companies router (F-NGX-COMPANIES).
Uses FastAPI TestClient with dependency_overrides to mock DB + auth.
"""
from unittest.mock import MagicMock, patch

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
    """Stand-in for AsyncSession. Companies list returned by execute().scalars().all()."""

    def __init__(self, companies=None):
        self._companies = companies or []
        self.added = []
        self.flushed = False
        self.committed = False

    async def execute(self, *args, **kwargs):
        result = MagicMock()
        result.scalars.return_value.all.return_value = self._companies
        result.fetchall.return_value = self._companies
        return result

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flushed = True

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        obj.id = 1

    async def rollback(self):
        pass

    async def close(self):
        pass


# Mutable container so the override can yield whatever we configure per test
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


@pytest.fixture
def anonymous_client():
    app.dependency_overrides.pop(get_current_user, None)
    yield TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: make_mock_user()


class TestListCompanies:
    def test_lists_all_companies(self, admin_client):
        _set_companies([
            make_mock_company("DANGCEM", "Dangote Cement Plc"),
            make_mock_company("GTCO", "Guaranty Trust Holding Co"),
        ])

        response = admin_client.get("/api/v1/companies")
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 2
        assert body["meta"]["total"] == 2
        assert body["error"] is None

    def test_filters_by_status(self, admin_client):
        _set_companies([make_mock_company("DANGCEM")])

        response = admin_client.get("/api/v1/companies?status=listed")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_searches_by_ticker(self, admin_client):
        _set_companies([make_mock_company("ZENITHBANK")])

        response = admin_client.get("/api/v1/companies?search=zenith")
        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_requires_authentication(self, anonymous_client):
        response = anonymous_client.get("/api/v1/companies")
        assert response.status_code == 401


class TestUploadCompaniesPdf:
    @patch("app.routers.companies.parse_ngx_companies_pdf")
    def test_upload_valid_pdf(self, mock_parse, admin_client):
        _set_companies([])
        mock_parse.return_value = [
            {"ticker": "DANGCEM", "name": "Dangote Cement Plc", "sector": "Industrial Goods"},
            {"ticker": "GTCO", "name": "Guaranty Trust Holding Co", "sector": "Banking"},
        ]

        response = admin_client.post(
            "/api/v1/companies/upload-pdf",
            files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["summary"]["total"] == 2
        assert body["data"]["summary"]["inserted"] == 2
        assert body["data"]["summary"]["updated"] == 0
        assert body["error"] is None
        assert _get_mock_db().committed

    @patch("app.routers.companies.parse_ngx_companies_pdf")
    def test_upload_updates_existing_company(self, mock_parse, admin_client):
        existing = make_mock_company("DANGCEM", "Dangote Cement Old Name")
        existing.sector = "Old Sector"
        _set_companies([existing])
        mock_parse.return_value = [
            {"ticker": "DANGCEM", "name": "Dangote Cement Plc", "sector": "Industrial Goods"},
        ]

        response = admin_client.post(
            "/api/v1/companies/upload-pdf",
            files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["summary"]["total"] == 1
        assert body["data"]["summary"]["inserted"] == 0
        assert body["data"]["summary"]["updated"] == 1

    def test_rejects_non_pdf(self, admin_client):
        response = admin_client.post(
            "/api/v1/companies/upload-pdf",
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert response.status_code == 422

    @patch("app.routers.companies.parse_ngx_companies_pdf")
    def test_returns_422_when_no_companies_found(self, mock_parse, admin_client):
        _set_companies([])
        mock_parse.return_value = []

        response = admin_client.post(
            "/api/v1/companies/upload-pdf",
            files={"file": ("empty.pdf", b"%PDF", "application/pdf")},
        )
        assert response.status_code == 422

    def test_requires_admin(self, readonly_client):
        response = readonly_client.post(
            "/api/v1/companies/upload-pdf",
            files={"file": ("test.pdf", b"fake", "application/pdf")},
        )
        assert response.status_code == 403


class TestDownloadTemplate:
    def test_download_template_returns_csv(self, admin_client):
        response = admin_client.get("/api/v1/companies/download-template")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "companies_template.csv" in response.headers["content-disposition"]

    def test_download_template_requires_admin(self, readonly_client):
        response = readonly_client.get("/api/v1/companies/download-template")
        assert response.status_code == 403
