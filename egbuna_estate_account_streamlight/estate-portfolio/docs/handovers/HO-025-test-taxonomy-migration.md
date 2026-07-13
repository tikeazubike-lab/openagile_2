---
type: HO
id: HO-025
title: Claude → Owl Alpha: Test Taxonomy Migration (Urgent)
date: 2026-06-25
from: Claude (The Brain)
to: Owl Alpha (Codex executor)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT — execute before writing any new tests
---

# HO-025 — Test Taxonomy Migration

## Context

A formal test taxonomy has been adopted from the Codex Test Architect
directive. All existing test files violate the new naming and folder
conventions. This migration must happen immediately — before any new
tests are written — or the codebase will have mixed conventions that
are impossible to navigate.

Full taxonomy spec: EPM_TEST_TAXONOMY.md

---

## 1. What Needs to Happen

### Step 1 — Create new folder structure

```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio

mkdir -p tests/backend/auth/login/{unit,integration,contract}
mkdir -p tests/backend/auth/logout/integration
mkdir -p tests/backend/holdings/create/{unit,integration,contract}
mkdir -p tests/backend/holdings/update/integration
mkdir -p tests/backend/holdings/delete/integration
mkdir -p tests/backend/holdings/publish/integration
mkdir -p tests/backend/prices/quick-entry/integration
mkdir -p tests/backend/prices/pdf-upload/{unit,integration}
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
mkdir -p tests/security/cookies
mkdir -p tests/infrastructure/docker
mkdir -p tests/infrastructure/traefik
mkdir -p tests/fixtures
```

### Step 2 — Move shared fixtures

```bash
# Move conftest.py to shared fixtures location
cp backend/tests/conftest.py tests/fixtures/conftest.py

# Create symlink or update imports in each test subdirectory
# Pytest will find conftest.py by traversing up the directory tree
# so placing it in tests/fixtures/ works if tests/ is the root
```

### Step 3 — Split and migrate existing test files

#### test_br001_gherkin.py → split into 4 files

```bash
# SC-001 to SC-006 (portfolio valuation / holdings)
# → tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py

# SC-007 to SC-014 (price entry)
# → tests/backend/prices/quick-entry/integration/PRIC-QUICK-BE-INT-001.py

# SC-015 to SC-020 (auth)
# → tests/backend/auth/login/integration/AUTH-LOGIN-BE-INT-001.py

# SC-021 to SC-024 (dividends)
# → tests/backend/dividends/integration/DIVD-CREATE-BE-INT-001.py
```

Each split file must open with this docstring pattern:

```python
"""
Test ID:     AUTH-LOGIN-BE-INT-001
Domain:      Authentication
Workflow:    Login
Layer:       Backend
Type:        Integration
Requirement: REQ-AUTH-001
Feature:     F-001 Authentication
Migrated from: backend/tests/test_br001_gherkin.py (SC-015 to SC-020)
"""
```

#### test_br001_gherkin_fr3_fr4.py → split into 2 files

```bash
# SC-025 to SC-031 (NAV History)
# → tests/backend/nav-history/integration/NAVH-SNAPSHOT-BE-INT-001.py

# SC-032 to SC-037 (XIRR)
# → tests/backend/holdings/update/integration/HOLD-XIRR-BE-INT-001.py
```

#### Remaining files — direct rename + relocate

```
backend/tests/test_auth_router.py
  → tests/backend/auth/login/integration/AUTH-LOGIN-BE-INT-001.py
    (merge with SC-015–020 from br001 — deduplicate overlapping scenarios)

backend/tests/test_deps.py
  → tests/backend/auth/login/unit/AUTH-LOGIN-BE-UT-001.py

backend/tests/test_holdings_integration.py
  → tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py
    (or split by workflow if it covers update/delete too)

backend/tests/test_registrars_integration.py (if exists)
  → tests/backend/registrars/crud/integration/REGR-CRUD-BE-INT-001.py

backend/tests/test_price_entry.py (if exists)
  → tests/backend/prices/quick-entry/integration/PRIC-QUICK-BE-INT-001.py
```

### Step 4 — Update pytest configuration

```ini
# pyproject.toml or pytest.ini
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

### Step 5 — Verify old location is empty

```bash
ls backend/tests/
# Should show only __init__.py or be empty
# If any .py files remain: they were missed in the migration

# Run full test suite from new location
docker compose -f docker-compose.v2.yml exec backend \
  pytest tests/backend/ -v --tb=short 2>&1 | tail -30
```

### Step 6 — Add new security smoke tests

These are gaps identified in the taxonomy review.
Write these as new files — do not migrate them from anywhere:

```python
# tests/security/authentication/jwt/SEC-JWT-BE-SEC-001.py
"""
Test ID:     SEC-JWT-BE-SEC-001
Domain:      Security
Workflow:    JWT Validation
Layer:       Backend / Security
Type:        Security Test
Requirement: REQ-SEC-001
"""

class TestJWTSecurity:

    async def test_SEC_JWT_BE_SEC_001_tampered_token_rejected(
        self, async_client
    ):
        """Tampered JWT signature returns 401"""
        response = await async_client.get(
            "/api/v1/holdings",
            cookies={"epm_token": "eyJ.tampered.signature"}
        )
        assert response.status_code == 401

    async def test_SEC_JWT_BE_SEC_002_missing_token_rejected(
        self, async_client
    ):
        """Request with no cookie returns 401"""
        response = await async_client.get("/api/v1/holdings")
        assert response.status_code == 401

    async def test_SEC_JWT_BE_SEC_003_cookie_is_httponly(
        self, async_client, test_admin_credentials
    ):
        """Login response sets HttpOnly cookie"""
        response = await async_client.post(
            "/api/v1/auth/login",
            json=test_admin_credentials
        )
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie
        assert "SameSite=Strict" in set_cookie or "samesite=strict" in set_cookie.lower()
        assert "Max-Age=2592000" in set_cookie or "max-age=2592000" in set_cookie.lower()


# tests/security/authorization/role-boundaries/SEC-ROLE-BE-SEC-001.py
"""
Test ID:     SEC-ROLE-BE-SEC-001
Domain:      Security
Workflow:    Role Boundary Enforcement
Layer:       Backend / Security
Type:        Security Test
Requirement: REQ-SEC-002
"""

class TestRoleBoundaries:

    async def test_SEC_ROLE_BE_SEC_001_readonly_cannot_create_holding(
        self, readonly_http_client
    ):
        """Read-only user gets 403 on POST /admin/holdings"""
        response = await readonly_http_client.post(
            "/api/v1/admin/holdings",
            json={"company_id": 1, "num_shares": 100,
                  "avg_purchase_price": "400.00"}
        )
        assert response.status_code == 403

    async def test_SEC_ROLE_BE_SEC_002_readonly_cannot_delete_holding(
        self, readonly_http_client
    ):
        """Read-only user gets 403 on DELETE"""
        response = await readonly_http_client.delete(
            "/api/v1/admin/holdings/1"
        )
        assert response.status_code == 403

    async def test_SEC_ROLE_BE_SEC_003_readonly_cannot_update_price(
        self, readonly_http_client
    ):
        """Read-only user gets 403 on price entry"""
        response = await readonly_http_client.post(
            "/api/v1/prices/quick",
            json={"company_id": 1, "price": "450.00",
                  "entry_date": "2026-06-25"}
        )
        assert response.status_code == 403
```

### Step 7 — Add infrastructure smoke test

```python
# tests/infrastructure/docker/INF-DOCKER-SMK-001.py
"""
Test ID:     INF-DOCKER-SMK-001
Domain:      Infrastructure
Workflow:    Docker Health Check
Layer:       Infrastructure
Type:        Smoke Test
"""
import httpx
import pytest

BASE_URL = "https://testdrive.epm.zubbystudio.shop"

class TestDockerSmoke:

    def test_INF_DOCKER_SMK_001_api_is_reachable(self):
        """Staging API returns a response (200 or 401 — not 5xx)"""
        response = httpx.get(f"{BASE_URL}/api/v1/holdings", timeout=10)
        assert response.status_code in (200, 401)
        # 401 = app is up, auth required. 200 = app up, somehow authed.
        # 5xx = app is down or crashed.

    def test_INF_DOCKER_SMK_002_frontend_is_served(self):
        """Staging frontend returns HTML"""
        response = httpx.get(BASE_URL, timeout=10)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
```

---

## 2. What Is Verified When Done

```bash
# All tests in new location:
docker compose -f docker-compose.v2.yml exec backend \
  pytest tests/ -v --co 2>&1 | grep "test session starts" -A 5

# No tests remain in old location:
find backend/tests/ -name "test_*.py" | wc -l
# Expected: 0

# New security tests pass:
docker compose -f docker-compose.v2.yml exec backend \
  pytest tests/security/ -v --tb=short

# Smoke test (run from outside container):
pytest tests/infrastructure/ -v --tb=short
```

---

## 3. Blockers

None. This migration is independent of all feature work.
Can be done in parallel with HO-024 frontend work (Nex N2).

---

## 4. After Migration

- Update .context/progress-tracker.md:
  Add entry: "Test taxonomy migration — COMPLETE"

- Write HO-026 to Claude confirming:
  - New folder structure in place
  - All existing tests migrated and passing
  - New security + smoke tests passing
  - pytest.ini updated

- The next test written for any feature must use the new taxonomy.
  No exceptions.
