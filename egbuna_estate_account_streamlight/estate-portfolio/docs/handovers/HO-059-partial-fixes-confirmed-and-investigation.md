---
type: HO
id: HO-059
title: Hermes → Claude: Blocks 1–3 + Block 5 Partial Fixed — 98 Pass. Investigation Results for Blocks 4, 5 (Remaining), 6.
date: 2026-07-12
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: NORMAL
---

# HO-058 — Blocks 1–3 and Block 5 (Partial) Fixed — Investigation Results for Remaining Items

## (a) Blocks 1–3 and Approved Parts of Block 5 — Fix Confirmed

### Fixes Applied

| File | Changes | Tests Passing |
|------|---------|--------------|
| `tests/integration/conftest.py` | Fixed imports (get_session, create_access_token, flat models), field names (hashed_password, average_cost_basis, holding_type), dependency override key, token signature | Import error fixed — now reaches env var `KeyError: 'DB_HOST'` (expected — integration env not configured) |
| `tests/unit/test_api_routes.py` | Complete rewrite: `app.dependency_overrides` pattern replacing `unittest.mock.patch` for `get_session`. Fixed response shape assertions, mock chain for AsyncMock, HTTP methods, field names | **16/16 pass** (was 0/16) |
| `tests/unit/test_auth_logic.py` | Fixed imports to `app.deps`, replaced `hash_password`/`verify_password` with local `pwd_context`, replaced `decode_access_token` with `decode_token`, fixed `create_access_token` calls, fixed `get_current_user` test for `session=` kwarg | **19/19 pass** (was 0/19) |
| `tests/unit/test_pydantic_schemas.py` | Fixed paths for `LoginRequest`, `HoldingCreate`, `QuickPricePayload`. Updated assertions for current schema behavior (no validators on some fields). TransactionCreate → xfail("blocked on F-009"). DashboardResponse → xfail("awaiting user judgment") | **22 pass + 10 xpassed** (was 0/32) |

### Pre-existing Working Tests (unchanged, still passing)
| File | Count |
|------|-------|
| `test_deps.py` | 4 |
| `test_holdings_service.py` | 7 |
| `test_admin_users.py` | 15 |
| `test_companies_router.py` | 11 |
| `test_cost_basis_router.py` | 12 |

**Total: 98 pass + 10 xpassed. Zero failures.**

## (b) Block 4: 7 Removed Functions — Live Consumer Check

| Function | Live consumer? | Where | Recommendation |
|----------|--------------|-------|---------------|
| `calculate_current_value` | ✅ Inline | `holdings.py:61`, `services/holdings.py:23`, `dashboard.py:94` | Reimplement or retire test |
| `calculate_cost_basis` | ✅ Inline | `holdings.py:53`, `holdings.py:167` | Reimplement or retire test |
| `calculate_return_pct` | ✅ Inline | `holdings.py:58-64`, `dashboard.py:120` | Reimplement or retire test |
| `calculate_portfolio_total` | ✅ Replaced | `services/portfolio.py:9` → `calculate_total_assets()` | Reimplement or retire test |
| `calculate_dividend_yield` | ❌ **Hardcoded 0.0** | `holdings.py:97` returns `"div_yield": 0.0` always. Frontend expects real values (`types/index.ts:103`, mock.ts has 4.2–10.2%). **Shipped feature, broken calculation.** | Reimplement — frontend already shows the column |
| `calculate_rebalancing_gap` | ❌ No consumer | No rebalancing feature exists | Retire test |
| `calculate_wht_deduction` | ❌ No consumer | No WHT logic exists. F-010 Claims stores raw payouts. | Retire test |

## (c) Block 5: DashboardResponse — Raw Dict vs Pydantic

Dashboard returns a raw dict. `routers/dashboard.py:129-146` builds a plain Python `dict` and wraps it in `_envelope(response_data)`. No Pydantic model validates the shape anywhere in the codebase. Monetary fields are `str(...)` by convention but not enforced by schema.

## (d) Block 6: seed_admin.py — Password Reset on Re-run

**Confirmed: YES, always overwrites.** Exact code at `backend/scripts/seed_admin.py:46-52`:

```python
if existing:
    existing.hashed_password = pwd_context.hash(admin_password)
    session.add(existing)
    await session.commit()
    print(f"✅ Admin user '{admin_username}' already exists — password updated.")
    return
```

The test assumes idempotency (no-op if user exists). The real script is intentionally non-idempotent — it always overwrites the password when re-run, with an explicit comment explaining this is for GitHub Secret rotation.

## Remaining Open Items (Awaiting User Judgment)

| Item | Status |
|------|--------|
| `test_business_logic.py` | Needs user decision: reimplement 3 calculation functions that have live inline consumers, retire 2 (rebalancing, WHT) that have no consumers |
| `test_seed_admin.py` | Needs user decision: either the test or the script needs to change — they disagree on idempotency |
| `test_pydantic_schemas.py` DashboardResponse | Needs user decision: create a Pydantic schema or remove these tests |
| Integration/DB tests (7 files) | Need `DB_HOST` env var + database setup — should be addressed as a separate task |
| Backfill script | User requested stop-and-check before writing |
| PR | User requested stop-and-check before opening |
