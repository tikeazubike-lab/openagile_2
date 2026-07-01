# EPM Test Taxonomy — Adoption + Migration Plan
**From**: Claude (The Brain)
**To**: Owl Alpha (Codex executor) + all agents
**Date**: 2026-06-25
**Protocol**: Codex Test Taxonomy v1.0 + EPM Hybrid Framework v1.0
**Priority**: Execute immediately — before writing any new tests

---

## Domain Codes for EPM

```
AUTH  = Authentication (login, logout, session, cookie)
HOLD  = Holdings (CRUD, publish, soft delete, admin)
PRIC  = Price Entry (quick, PDF, CSV, audit, revert)
PRIH  = Price History (chart, filter, table)
DASH  = Dashboard (KPIs, charts, bell, action items)
REGR  = Registrars (CRUD, documents, requirements, linking)
CLAM  = Claims (AMCON/CAC tracking, ClaimRecord)
DIVD  = Dividends (CRUD, annual summary, WHT)
TRAN  = Transactions (CRUD, auto-generate)
NAVH  = NAV History (snapshot, APScheduler)
WTCH  = Watchlist (tracking, target price)
COMP  = Companies (NGX scrape, filter, profile)
ADMN  = Admin Section (audit log, CRUD hub)
USER  = User Management (roles, permissions)
OBSD  = Obsidian Import (vault sync, import script)
CHAT  = AI ChatBot (intent router, response)
SEC   = Security (JWT, cookies, CSRF, auth boundaries)
INF   = Infrastructure (Docker, Traefik, health checks)
```

---

## Test Identifier Standard

```
<DOMAIN>-<WORKFLOW>-<LAYER>-<TYPE>-<NNN>

Examples:
  AUTH-LOGIN-BE-INT-001      login endpoint integration test
  AUTH-LOGIN-FE-E2E-001      login flow end-to-end
  AUTH-LOGOUT-BE-INT-001     logout endpoint integration
  HOLD-CREATE-BE-INT-001     create holding integration
  HOLD-CREATE-BE-API-001     create holding contract/schema test
  PRIC-PDF-BE-INT-001        PDF upload integration
  PRIC-PDF-BE-UT-001         PDF parser unit test
  DASH-CHART-FE-E2E-001      dashboard chart rendering E2E
  SEC-JWT-BE-SEC-001         JWT validation security test
  INF-DOCKER-SMK-001         Docker health check smoke test
```

---

## New Folder Structure

```
tests/
├── backend/
│   ├── auth/
│   │   ├── login/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── contract/
│   │   └── logout/
│   │       ├── unit/
│   │       └── integration/
│   ├── holdings/
│   │   ├── create/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── contract/
│   │   ├── update/
│   │   ├── delete/
│   │   └── publish/
│   ├── prices/
│   │   ├── quick-entry/
│   │   ├── pdf-upload/
│   │   ├── csv-import/
│   │   └── audit/
│   ├── dashboard/
│   │   └── kpis/
│   ├── registrars/
│   │   ├── crud/
│   │   ├── documents/
│   │   └── requirements/
│   ├── claims/
│   ├── dividends/
│   ├── nav-history/
│   ├── admin/
│   │   └── audit/
│   └── companies/
│
├── frontend/
│   ├── auth/
│   │   ├── login/
│   │   └── logout/
│   ├── holdings/
│   ├── dashboard/
│   ├── prices/
│   ├── registrars/
│   └── admin/
│
├── security/
│   ├── authentication/
│   │   └── jwt/
│   ├── authorization/
│   │   └── role-boundaries/
│   ├── cookies/
│   └── input-validation/
│
├── infrastructure/
│   ├── docker/
│   ├── traefik/
│   └── health-checks/
│
├── fixtures/
│   ├── conftest.py          ← shared pytest fixtures (all backend tests)
│   ├── factories.py         ← model factories (Company, Holding, User, etc.)
│   └── seed_data.py         ← minimal seed for test runs
│
└── requirements.txt         ← test-only dependencies
```

---

## Existing File Migration Map

Map every current file to its new location and rename:

### backend/tests/ → tests/backend/

| Current File | New Location | New Name |
|-------------|-------------|---------|
| test_br001_gherkin.py | tests/backend/holdings/create/integration/ | AUTH-LOGIN-BE-INT-001.py → split (see below) |
| test_holdings_integration.py | tests/backend/holdings/ | split by workflow |
| test_auth_router.py | tests/backend/auth/login/integration/ | AUTH-LOGIN-BE-INT-001.py |
| test_deps.py | tests/backend/auth/login/unit/ | AUTH-LOGIN-BE-UT-001.py |
| test_br001_gherkin_fr3_fr4.py | tests/backend/nav-history/ + prices/ | split |

### Detailed Split Instructions

**test_br001_gherkin.py** contains mixed concerns — split as:
```
SC-001 to SC-006 (portfolio valuation) → tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py
SC-007 to SC-014 (price entry)         → tests/backend/prices/quick-entry/integration/PRIC-QUICK-BE-INT-001.py
SC-015 to SC-020 (auth)               → tests/backend/auth/login/integration/AUTH-LOGIN-BE-INT-001.py
SC-021 to SC-024 (dividends)          → tests/backend/dividends/integration/DIVD-CREATE-BE-INT-001.py
```

**test_br001_gherkin_fr3_fr4.py** — split as:
```
SC-025 to SC-031 (NAV History)  → tests/backend/nav-history/integration/NAVH-SNAPSHOT-BE-INT-001.py
SC-032 to SC-037 (XIRR)        → tests/backend/holdings/update/integration/HOLD-UPDATE-BE-INT-001.py
```

---

## Requirement Traceability Matrix

```
REQ-AUTH-001 (30-day persistent login)
  ├── AUTH-LOGIN-BE-INT-001   (cookie max_age=2592000)
  ├── AUTH-LOGIN-BE-API-001   (Set-Cookie header contract)
  └── SEC-JWT-BE-SEC-001      (cookie httpOnly, SameSite)

REQ-HOLD-001 (holdings CRUD)
  ├── HOLD-CREATE-BE-INT-001  (POST creates record + audit)
  ├── HOLD-UPDATE-BE-INT-001  (PATCH updates correctly)
  ├── HOLD-DELETE-BE-INT-001  (soft delete only)
  └── HOLD-CREATE-FE-E2E-001  (admin drawer end-to-end)

REQ-PRIC-001 (NGX PDF price update)
  ├── PRIC-PDF-BE-UT-001      (parser unit test)
  ├── PRIC-PDF-BE-INT-001     (upload endpoint integration)
  └── PRIC-PDF-BE-API-001     (response contract)

REQ-SEC-001 (role enforcement)
  ├── SEC-ROLE-BE-SEC-001     (readonly cannot write)
  ├── SEC-ROLE-BE-SEC-002     (admin routes return 403 for readonly)
  └── AUTH-LOGOUT-BE-INT-001  (logout clears cookie)
```

---

## Migration Execution — Owl Alpha

Run in this exact order. Do not skip steps.

```bash
# Step 1 — Create new folder structure
cd /home/zubbyik/openagile_2/.../estate-portfolio
mkdir -p tests/backend/auth/login/unit
mkdir -p tests/backend/auth/login/integration
mkdir -p tests/backend/auth/login/contract
mkdir -p tests/backend/auth/logout/integration
mkdir -p tests/backend/holdings/create/unit
mkdir -p tests/backend/holdings/create/integration
mkdir -p tests/backend/holdings/create/contract
mkdir -p tests/backend/holdings/update/integration
mkdir -p tests/backend/holdings/delete/integration
mkdir -p tests/backend/holdings/publish/integration
mkdir -p tests/backend/prices/quick-entry/integration
mkdir -p tests/backend/prices/pdf-upload/unit
mkdir -p tests/backend/prices/pdf-upload/integration
mkdir -p tests/backend/prices/csv-import/integration
mkdir -p tests/backend/prices/audit/integration
mkdir -p tests/backend/dashboard/kpis/integration
mkdir -p tests/backend/registrars/crud/integration
mkdir -p tests/backend/registrars/documents/integration
mkdir -p tests/backend/registrars/requirements/integration
mkdir -p tests/backend/claims/integration
mkdir -p tests/backend/dividends/integration
mkdir -p tests/backend/nav-history/integration
mkdir -p tests/backend/admin/audit/integration
mkdir -p tests/backend/companies/integration
mkdir -p tests/frontend/auth/login
mkdir -p tests/frontend/holdings
mkdir -p tests/frontend/dashboard
mkdir -p tests/security/authentication/jwt
mkdir -p tests/security/authorization/role-boundaries
mkdir -p tests/infrastructure/docker
mkdir -p tests/fixtures

# Step 2 — Move shared conftest
mv backend/tests/conftest.py tests/fixtures/conftest.py

# Step 3 — Split and rename test files per migration map above
# (Do each file manually — do not bulk move without splitting)

# Step 4 — Verify no tests remain in old location
ls backend/tests/
# Should be empty (or only __init__.py)

# Step 5 — Run all tests from new location to confirm nothing broke
docker compose exec backend pytest tests/backend/ -v --tb=short

# Step 6 — Update pytest.ini or pyproject.toml testpaths
# Change: testpaths = ["backend/tests"]
# To:     testpaths = ["tests/backend", "tests/security", "tests/infrastructure"]
```

---

## New Test File Template

Every new test file follows this structure:

```python
"""
Test ID:     HOLD-CREATE-BE-INT-001
Domain:      Holdings
Workflow:    Create
Layer:       Backend
Type:        Integration
Requirement: REQ-HOLD-001
Feature:     F-003 Holdings

Description:
    Tests that POST /api/v1/admin/holdings creates a holding record
    correctly, writes an admin_audit entry, and returns the correct
    API contract shape.
"""
import pytest
from decimal import Decimal
from httpx import AsyncClient


class TestHoldCreate:

    @pytest.mark.asyncio
    async def test_HOLD_CREATE_BE_INT_001(
        self, admin_http_client: AsyncClient, test_company, db_session
    ):
        """
        REQ-HOLD-001 | F-003 | SC-028
        Given a valid company exists
        When admin POSTs /api/v1/admin/holdings with valid payload
        Then holding is created with status='draft'
        And admin_audit record is created with action='CREATE'
        """
        response = await admin_http_client.post(
            "/api/v1/admin/holdings",
            json={
                "company_id": test_company.id,
                "num_shares": 100,
                "avg_purchase_price": "400.00",
                "status": "draft",
            }
        )

        # REQ-HOLD-001 | Then status 201
        assert response.status_code == 201

        data = response.json()["data"]

        # REQ-HOLD-001 | And status is draft
        assert data["status"] == "draft"

        # REQ-HOLD-001 | And avg_purchase_price is string (monetary contract)
        assert isinstance(data["avg_purchase_price"], str)
```

---

## Coverage Gaps (Current State)

These domains have zero test coverage — add when feature is built:

```
ADMN-AUDIT     — admin_audit table and GET /admin/audit endpoint
USER-CREATE    — user management (F-016)
USER-ROLE      — role assignment and enforcement (F-016)
CHAT-INTENT    — chatbot intent routing (F-022)
SEC-ROLE       — role boundary security tests (readonly cannot write)
SEC-JWT        — JWT validation and cookie security
INF-DOCKER     — container health check smoke tests
```

---

## pytest.ini Update

```ini
[pytest]
asyncio_mode = auto
testpaths =
    tests/backend
    tests/security
    tests/infrastructure
python_files = *.py
python_classes = Test*
python_functions = test_*
```
