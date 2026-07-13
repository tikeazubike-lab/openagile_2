---
type: HO
id: HO-058
title: Hermes → Claude: Test Suite Investigation — 6 Broken Import Blocks Resolved (Investigation Only)
date: 2026-07-12
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-058 — Test Suite Investigation Findings

## Preamble

This handover reports the investigation into 6 broken import blocks in the
backend test suite. Per Zubbyik's instruction: **no code was changed**.
Findings are presented exactly; fixes await approval.

---

## (a) Blocks 1–3 — Fix Status

**Not yet applied.** Investigation identified exactly what needs to change
for each. Changes are ready to write on approval.

### Block 1: `tests/integration/conftest.py`

| Issue | Current | Target |
|-------|---------|--------|
| Import `get_db` | `app.database.get_db` (doesn't exist) | `app.deps.get_session` |
| Import `create_access_token` | `app.auth.logic.create_access_token` (doesn't exist) | `app.deps.create_access_token` |
| Import `hash_password` | `app.auth.logic.hash_password` (doesn't exist) | Replace with local `pwd_context = CryptContext(schemes=["bcrypt"])` |
| Import `User` | `app.models.users.User` (doesn't exist) | `app.models.User` |
| Import `Company` (inline L173) | `app.models.companies.Company` (doesn't exist) | `app.models.Company` |
| Import `Holding` (inline L187) | `app.models.holdings.Holding` (doesn't exist) | `app.models.Holding` |
| `create_access_token` call | `data={"sub": ..., "role": ...}` | `(user_id=1, role="admin")` |
| Dependency override key | `get_db` | `get_session` |
| `User( password_hash=... )` | `password_hash=` (doesn't exist) | `hashed_password=` |
| `Holding( avg_purchase_price=..., status=... )` | Old field names | `average_cost_basis=`, `holding_type=` |
| Missing fields | — | Add `total_cost` to Holding fixtures |

### Block 2: `tests/unit/test_api_routes.py`

| Issue | Current | Target |
|-------|---------|--------|
| Import `create_access_token` | `app.auth.logic` | `app.deps` |
| Import `hash_password` | `app.auth.logic` | Remove — hash no longer exposed |
| `make_token()` | `data={"sub": ..., "role": ...}` | `(user_id=1, role=...)` |
| `make_mock_user()` | `password_hash = hash_password(...)` | `hashed_password = "$2b$..."` (hardcoded bcrypt stub) |
| `make_mock_holding()` | `ticker`, `company_name`, `avg_purchase_price`, `current_price`, `status`, `deleted_at` | Must match current `Holding` model fields |
| All `patch("app.routers.{X}.get_db", ...)` | `get_db` (doesn't exist) | `get_session` |
| `patch("app.routers.auth.verify_password", ...)` | `verify_password` (doesn't exist) | `pwd_context.verify` — path: `app.routers.auth.pwd_context.verify` |

### Block 3: `tests/unit/test_auth_logic.py`

| Issue | Current | Target |
|-------|---------|--------|
| Import `create_access_token` | `app.auth.logic` | `app.deps` — sig change: `(user_id, role)` not `(data=dict)` |
| Import `decode_access_token` | `app.auth.logic` (doesn't exist) | `app.deps.decode_token` — same signature `(token: str)`, same error pattern |
| Import `hash_password` | `app.auth.logic` (doesn't exist) | Replace with local `pwd_context.hash()` |
| Import `verify_password` | `app.auth.logic` (doesn't exist) | Replace with local `pwd_context.verify()` |
| Import `get_current_user` | `app.auth.dependencies` (doesn't exist) | `app.deps.get_current_user` — same signature |
| Import `require_admin` | `app.auth.dependencies` (doesn't exist) | `app.deps.require_admin` — same signature |
| Test calls `get_current_user(epm_token=token, db=mock_db)` | `db=` keyword | `session=` keyword |
| `patch("app.auth.dependencies.get_db", ...)` | Stale path | Must use direct call, not patch (test calls function directly, not through DI) |
| `settings.jwt_secret` | Attribute name | `settings.JWT_SECRET` |

---

## (b) Block 4: `test_business_logic.py` — 7 Removed Functions — Live Consumer Check

### `calculate_current_value(shares, current_price) → shares × price`
- **Live consumer**: ✅ Yes, inline in multiple locations
  - `routers/holdings.py:61` — `h.num_shares * h.company.current_price`
  - `services/holdings.py:23` — `shares * price`
  - `routers/dashboard.py:94` — reads `h.current_value` (precomputed)
- **Consumer ships today**: Yes — holdings list, dashboard, price recalc

### `calculate_cost_basis(shares, avg_price) → shares × price`
- **Live consumer**: ✅ Yes, inline
  - `routers/holdings.py:53` — `h.num_shares * h.average_cost_basis`
  - `routers/holdings.py:167` — `Decimal(num_shares) * Decimal(avg_purchase_price)`
- **Consumer ships today**: Yes — holdings list, holding creation

### `calculate_return_pct(current, cost) → ((current - cost) / cost) × 100`
- **Live consumer**: ✅ Yes, inline
  - `routers/holdings.py:58-64` — `(current_value - eff_cost) / eff_cost * 100`
  - `routers/dashboard.py:120` — `(val - cost) / cost * 100`
- **Consumer ships today**: Yes — holdings list `return_pct`, dashboard top holdings

### `calculate_portfolio_total(holdings) → sum of live values`
- **Live consumer**: ✅ Yes, replaced
  - `services/portfolio.py:9` — `calculate_total_assets(active_holdings, claim_records)`
  - Different signature, same purpose
- **Consumer ships today**: Yes — dashboard

### `calculate_dividend_yield(annual_dividend, current_price) → (div / price) × 100`
- **Live consumer**: ❌ **Hardcoded to 0.0 in production**
  - `routers/holdings.py:97` — `"div_yield": 0.0` — **always returns zero**
  - The frontend expects a real `div_yield` value: `types/index.ts:103` declares `div_yield: number`, holdings table column renders it, mock data has realistic values (4.2, 8.1, etc.)
  - But the backend never computes it — no dividend yield function exists
  - This is a **genuine gap**: the frontend field and user story exist, but the backend always returns 0.0
- **Recommendation**: Not retired — should be reimplemented. The feature is shipped (frontend shows the column); the calculation just wasn't wired.

### `calculate_rebalancing_gap(current_pct, target_pct) → current - target`
- **Live consumer**: ❌ **No consumer exists**
  - No rebalancing logic anywhere in the backend
  - Route `/rebalancing` is a frontend stub page
- **Recommendation**: Eligible for retirement — rebalancing feature does not exist yet.

### `calculate_wht_deduction(gross, rate) → (net, wht)`
- **Live consumer**: ❌ **No consumer exists**
  - No WHT/deduction logic anywhere in the backend
  - F-010 Claims stores `expected_payout` and `actual_payout` directly on `ClaimRecord` — no gross→net deduction step
  - The test checked: `gross=100000, rate=10% → net=90000, wht=10000`
- **Recommendation**: Eligible for retirement — no WHT feature exists or is planned in F-010's scope.

---

## (c) Block 5: `test_pydantic_schemas.py` — DashboardResponse

### `DashboardResponse`
- **Raw dict**: `routers/dashboard.py:129-146` builds a plain Python `dict` and wraps it with `_envelope(response_data)`. No Pydantic model validates the response shape.
- **No Pydantic model exists** anywhere in the codebase for dashboard responses.
- **What the test checked**: monetary fields (`total_portfolio_value`, `active_portfolio_value`, etc.) must be strings, not floats. The current dashboard returns these as `str(...)` — so the convention is correct, just not enforced by a schema.

### Other schemas in this file

| Schema | Exists? | Location | Fixable? |
|--------|---------|----------|----------|
| `LoginRequest` | ✅ Yes | `app/routers/auth.py:33` | Fix path |
| `HoldingCreate` | ✅ Yes | `app/routers/holdings.py:143` | Fix path |
| `PriceQuickEntry` | ❌ No | Renamed to `QuickPricePayload` at `app/routers/prices.py:19` | Rename + fix path |
| `TransactionCreate` | ❌ No | Does not exist anywhere | Mark xfail "blocked on F-009" |
| `DashboardResponse` | ❌ No | Does not exist anywhere | Needs user judgment |

---

## (d) Block 6: `test_seed_admin.py` — Password Reset Behavior

Confirmed by reading `backend/scripts/seed_admin.py` (67 lines). Here is the
exact logic at lines 40-52:

```python
async with AsyncSessionLocal() as session:
    result = await session.execute(
        select(User).where(User.username == admin_username)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update password for existing user if script runs again
        existing.hashed_password = pwd_context.hash(admin_password)
        session.add(existing)
        await session.commit()
        print(f"✅ Admin user '{admin_username}' already exists — password updated.")
        return

    user = User(
        username=admin_username,
        name=admin_name,
        hashed_password=pwd_context.hash(admin_password),
        role="admin",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    print(f"✅ Admin user '{admin_username}' created successfully.")
```

**Yes — the script ALWAYS overwrites the password on re-run.** The comment
at line 47 explicitly says "Update password for existing user if script
runs again (e.g. when GitHub Secret is updated)."

The test assumes idempotency (no-op if user exists), but the real script is
intentionally non-idempotent regarding the password. Relevant differences:

| Aspect | Test assumes | Reality |
|--------|-------------|---------|
| Function name | `seed_admin_user(session)` | `seed()` — no session param, creates own |
| Location | `app.scripts.seed_admin` | `backend/scripts/seed_admin.py` (outside `app/`) |
| Env var names | `ADMIN_USERNAME`, `ADMIN_PASSWORD` | `EPM_ADMIN_USERNAME`, `EPM_ADMIN_PASSWORD` |
| Re-run behavior | idempotent (does nothing) | overwrites password |
| Password plumbing | `verify_password()` | `pwd_context.verify()` inline |
| Module structure | `app.auth.logic` | Auth lives in `app/deps.py` + `app/routers/auth.py` |

---

## Raw Command Output

```
$ docker exec estate_portfolio_v3 python3 -m pytest tests/ --collect-only -q 2>&1 | grep "ERROR"
  ERROR tests/integration - ImportError: cannot import name 'get_db' from 'app.database'
  ERROR tests/unit/test_api_routes.py - ModuleNotFoundError: No module named 'app.auth'
  ERROR tests/unit/test_auth_logic.py - ModuleNotFoundError: No module named 'app.auth'
  ERROR tests/unit/test_business_logic.py - ImportError: cannot import name 'calculate_cost_basis'
  ERROR tests/unit/test_pydantic_schemas.py - ModuleNotFoundError: No module named 'app.schemas'
  ERROR tests/unit/test_seed_admin.py - ModuleNotFoundError: No module named 'app.scripts'

$ docker exec estate_portfolio_v3 python3 -m pytest tests/unit/test_deps.py tests/unit/test_holdings_service.py tests/unit/test_admin_users.py tests/unit/test_companies_router.py tests/unit/test_cost_basis_router.py -v --tb=no 2>&1 | tail -1
  → 49 passed
```
